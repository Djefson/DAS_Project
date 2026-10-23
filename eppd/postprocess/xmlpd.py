"""XML output parser for EnergyPlus results."""

from pathlib import Path
from types import SimpleNamespace
from xml.etree.ElementTree import parse

import pandas as pd
from xmljson import parker as pr

from ..logger import get_logger

logger = get_logger(__name__)




class Xmlpd:
    """Parser for EnergyPlus XML summary output (eplustbl.xml)."""

    def __init__(self, filepath: str | Path):
        self.filepath = Path(filepath)

        if not self.filepath.exists():
            raise SystemExit(f"XML file not found: {self.filepath}")

        logger.debug(f"Parsing XML output: {self.filepath.name}")

        try:
            tree = parse(self.filepath)
            self.root = tree.getroot()
        except Exception as e:
            raise ValueError(
                f"Failed to parse XML file {self.filepath}: {e}"
            ) from e

    def get_end_use_energy(self) -> pd.DataFrame:
        """AnnualBuildingUtilityPerformanceSummary EndUses table by fuel type."""
        summary = self.root.find('AnnualBuildingUtilityPerformanceSummary')
        end_uses = summary.findall('EndUses')[:-1]  # Exclude total row

        categories = [e.find('name').text for e in end_uses]

        # Extract energy by fuel type (no unit conversion)
        electricity = pd.Series(
            [float(e.find('Electricity').text) for e in end_uses],
            index=categories
        )

        natural_gas = pd.Series(
            [float(e.find('NaturalGas').text) for e in end_uses],
            index=categories
        )

        dist_cool = pd.Series(
            [float(e.find('DistrictCooling').text) for e in end_uses],
            index=categories
        )

        dist_heat_water = pd.Series(
            [float(e.find('DistrictHeatingWater').text) for e in end_uses],
            index=categories
        )

        dist_heat_steam = pd.Series(
            [float(e.find('DistrictHeatingSteam').text) for e in end_uses],
            index=categories
        )

        result = pd.DataFrame({
            'Electricity': electricity,
            'NaturalGas': natural_gas,
            'DistrictCooling': dist_cool,
            'DistrictHeatingWater': dist_heat_water,
            'DistrictHeatingSteam': dist_heat_steam
        })

        logger.debug(f"Extracted end-use energy: {len(categories)} categories")
        return result


    def get_eui_dist(self) -> pd.Series:
        """AnnualBuildingUtilityPerformanceSummary EndUses summed across fuels normalized by conditioned floor area."""
        annual_summary = self.root.find('AnnualBuildingUtilityPerformanceSummary')
        s = pd.DataFrame(pr.data(annual_summary)['EndUses']).set_index('name')
        eui_dist = s.sum(axis=1)
        bld_area = annual_summary.find('BuildingArea').find("NetConditionedBuildingArea").text

        return eui_dist / float(bld_area)

    def get_area(self) -> pd.Series:
        """conditioned floor area."""
        annual_summary = self.root.find('AnnualBuildingUtilityPerformanceSummary')
        bld_area = annual_summary.find('BuildingArea').find("NetConditionedBuildingArea").text

        return float(bld_area)



    def get_envelope_details(self) -> pd.DataFrame:
        """EnvelopeSummary OpaqueExterior table grouped by construction."""
        gr = pd.DataFrame(pr.data(self.root.find('EnvelopeSummary'))['OpaqueExterior']).groupby('Construction')
        opaque_env = gr.sum()[['NetArea', 'GrossArea']]
        opaque_env['UfactorWithFilm'] = gr.first()['UFactorWithFilm']
        return opaque_env

    def get_fenestration_details(self) -> pd.DataFrame:
        """EnvelopeSummary ExteriorFenestration table grouped by construction."""
        gr = pd.DataFrame(pr.data(self.root.find('EnvelopeSummary'))['ExteriorFenestration']).groupby('Construction')
        fen = gr.sum()[['AreaOfOneOpening', 'AreaOfMultipliedOpenings']]
        fen[['GlassUFactor', 'GlassShgc', 'GlassVisibleTransmittance']] = gr.first()[['GlassUFactor', 'GlassShgc', 'GlassVisibleTransmittance']]
        try:
            fen[['AssemblyUFactor', 'AssemblyShgc', 'AssemblyVisibleTransmittance']] = gr.first()[['AssemblyUFactor', 'AssemblyShgc', 'AssemblyVisibleTransmittance']]
        except KeyError:
            pass
        return fen


    def get_eui(self) -> float:
        """AnnualBuildingUtilityPerformanceSummary site EUI (energy per total building area)."""
        summary = self.root.find('AnnualBuildingUtilityPerformanceSummary')
        eui = float(summary.findall('SiteAndSourceEnergy')[1].find('EnergyPerTotalBuildingArea').text)
        logger.debug(f"Extracted EUI: {eui:.2f} kBtu/ft²")
        return eui

    def get_unmet_hours(self) -> pd.Series:
        """SystemSummary TimeSetpointNotMet totals."""
        return pd.Series(pr.data(self.root.find('SystemSummary').findall('TimeSetpointNotMet')[-1]))[1:]

    def get_unmet_zones(self, limit: int = 0) -> pd.DataFrame:
        """SystemSummary TimeSetpointNotMet by zone, filtered to values above limit."""
        data = pr.data(self.root.find('SystemSummary'))

        # Get TimeSetpointNotMet list, excluding the last element (summary row)
        unmetall = pd.DataFrame(data['TimeSetpointNotMet'][:-1]).set_index('name')

        # Filter data to return unmethours greater than limit.
        return unmetall[unmetall > limit].dropna(how='all').dropna(how='all', axis=1)

    def get_standard_results(self) -> pd.Series:
        """Combined series of end-use energy, peak demand, unmet hours, and EUI."""
        # Annual energy use
        annual_summary = self.root.find('AnnualBuildingUtilityPerformanceSummary')
        s = pd.DataFrame(pr.data(annual_summary)['EndUses'][:-1]).set_index('name')

        # Extract raw values (no unit conversion)
        s = s.loc[:, ['Electricity', 'NaturalGas', 'DistrictCooling',
                     'DistrictHeatingWater', 'DistrictHeatingSteam']]

        # Reshape to single series
        s = s.reset_index().melt(id_vars='name')
        s = s[s['value'] > 0]
        s = s.set_index(s.name + '_' + s.variable)['value']

        # Peak demand
        demand_summary = self.root.find('DemandEndUseComponentsSummary')
        sd = pd.DataFrame(pr.data(demand_summary)['EndUses'][:-1]).set_index('name')
        sd = sd.loc[:, ['Electricity', 'NaturalGas', 'DistrictCooling',
                       'DistrictHeatingWater', 'DistrictHeatingSteam']][1:]

        sd = sd.reset_index().melt(id_vars='name')
        sd = sd[sd['value'] > 0]
        sd = sd.set_index(sd.name + '_' + sd.variable + '_demand')['value']

        # Unmet hours
        unmet_section = self.root.find('SystemSummary').findall('TimeSetpointNotMet')[-1]
        unmet = pd.Series(pr.data(unmet_section))[1:]

        # EUI
        s['EUI'] = self.get_eui()

        # Combine all metrics
        return pd.concat([s, sd, unmet])

    def load_monthly_reports(self) -> None:
        """Load CustomMonthlyReport tables from XML as DataFrame attributes on self."""
        try:
            data = pr.data(self.root)
            loaded_count = 0

            for section_name, section_data in data.items():
                if 'monthly' not in section_name.lower():
                    continue

                # Handle list of monthly reports (multiple zones)
                if isinstance(section_data, list):
                    combined_df = pd.DataFrame()

                    for report in section_data:
                        if 'CustomMonthlyReport' not in report:
                            continue

                        df = pd.DataFrame(report['CustomMonthlyReport'])
                        df['zone'] = report.get('for', 'Unknown')
                        combined_df = pd.concat([combined_df, df], sort=True)

                    if not combined_df.empty:
                        combined_df = combined_df.set_index(['zone', 'name'])
                        setattr(self, section_name, combined_df)
                        loaded_count += 1

                # Handle single monthly report
                elif isinstance(section_data, dict):
                    if 'CustomMonthlyReport' in section_data:
                        df = pd.DataFrame(section_data['CustomMonthlyReport'])
                        setattr(self, section_name, df)
                        loaded_count += 1

            if loaded_count > 0:
                logger.debug(f"Loaded {loaded_count} monthly report(s)")
            else:
                logger.debug("No monthly reports found in XML output")

        except Exception as e:
            logger.warning(f"Failed to load monthly reports: {e}")


    def get_prm(
        self,
        custom_indices: list[tuple[str, str]] | None = None
    ) -> pd.DataFrame | pd.Series:
        """LeedSummary EAp2-4/5 Performance Rating Method Compliance table."""
        prm = pd.DataFrame(
            pr.data(self.root.find('LeedSummary'))['Eap245PerformanceRatingMethodCompliance']
        ).set_index('name')

        if custom_indices is None:
            return prm
        else:
            return prm.stack().loc[custom_indices]


    def get_input_verification_summary(self) -> pd.Series:
        """InputVerificationAndResultsSummary WindowWallRatio, SpaceTypeSummary, and SkylightRoofRatio."""
        input_verification = pr.data(self.root.find('InputVerificationAndResultsSummary'))

        wwr = pd.DataFrame(input_verification['WindowWallRatio']).set_index('name').stack()
        bldarea = pd.DataFrame(input_verification['SpaceTypeSummary']).set_index('name').stack()
        srr = pd.Series(input_verification['SkylightRoofRatio'])[1:]
        srr = pd.concat([srr],keys=['Roof'])

        return pd.concat([wwr,bldarea,srr])


    def get_system_summary_tables(self) -> None:
        """Load all SystemSummary tables as DataFrame attributes on self.SystemSummary namespace."""
        section_data = pr.data(self.root.find('SystemSummary'))

        # Remove notes and footnotes
        for key in ['for', 'note', 'footnote', 'General']:
            section_data.pop(key, None)

        # Create SystemSummary namespace
        setattr(self, 'SystemSummary', SimpleNamespace())
        section_obj = getattr(self, 'SystemSummary')

        loaded_count = 0
        for table_name, table_data in section_data.items():
            table_attr_name = table_name.replace(':', '_')

            if isinstance(table_data, list):
                # Handle list of records (exclude last if it's a summary row)
                df = pd.DataFrame(table_data).set_index('name')
                setattr(section_obj, table_attr_name, df)
                loaded_count += 1
            else:
                # Handle single record or series
                series = pd.Series(table_data)
                setattr(section_obj, table_attr_name, series)
                loaded_count += 1

        logger.debug(f"Loaded {loaded_count} SystemSummary table(s)")

    def load_all_tables(self) -> None:
        """Load all XML section tables as DataFrame attributes on per-section namespaces (excludes monthly reports)."""
        data = pr.data(self.root)
        loaded_count = 0

        # Remove metadata
        for key in ['BuildingName', 'EnvironmentName', 'WeatherFileLocationTitle',
                   'ProgramVersion', 'SimulationTimestamp']:
            data.pop(key, None)

        # Convert tables to DataFrames and set as attributes
        for section_name, section_data in data.items():
            if section_name in ['monthly', 'TariffReport']:
                continue

            # Remove notes and footnotes
            if isinstance(section_data, dict):
                for key in ['for', 'note', 'footnote', 'General']:
                    section_data.pop(key, None)

                # Create section namespace if it doesn't exist
                if not hasattr(self, section_name):
                    setattr(self, section_name, SimpleNamespace())
                section_obj = getattr(self, section_name)

                for table_name, table_data in section_data.items():
                    table_attr_name = table_name.replace(':', '_')

                    if isinstance(table_data, list):
                        df = pd.DataFrame(table_data).set_index('name')
                        setattr(section_obj, table_attr_name, df)
                        loaded_count += 1
                    else:
                        series = pd.Series(table_data)
                        setattr(section_obj, table_attr_name, series)
                        loaded_count += 1

        logger.debug(f"Loaded {loaded_count} standard table(s)")


def read_xml(filepath: str | Path) -> Xmlpd:
    """Parse EnergyPlus XML summary output file (eplustbl.xml).

    Args:
        filepath: Path to eplustbl.xml

    Example:
        >>> p = read_xml('path/to/eplustbl.xml')
        >>> p.get_end_use_energy()
        >>> p.get_eui()

    Returns Xmlpd object. currenly available methods:
        get_end_use_energy()        — annual energy by end-use and fuel
        get_eui()                   — site EUI
        get_eui_dist()              — EUI by end-use category
        get_unmet_hours()           — unmet heating/cooling hours total
        get_unmet_zones(limit)      — unmet hours by zone above limit
        get_envelope_details()      — opaque envelope U-values by construction
        get_fenestration_details()  — window properties by construction
        get_standard_results()      — combined energy, demand, unmet, EUI series
        get_prm()                   — LEED EAp2-4/5 PRM compliance table
        get_input_verification_summary() — WWR, floor area, SRR summary
        load_monthly_reports()      — load custom monthly reports as attributes
        get_system_summary_tables() — load SystemSummary tables as attributes
        load_all_tables()           — load all available XML tables as attributes
    """
    return Xmlpd(filepath)
