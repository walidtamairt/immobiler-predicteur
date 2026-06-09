import { useEffect, useState } from "react";
import MarketFilters from "../components/market/MarketFilters";
import KpiCards from "../components/market/KpiCards";
import PriceByNeighborhoodChart from "../components/market/PriceByNeighborhoodChart";
import PriceDistributionChart from "../components/market/PriceDistributionChart";
import PriceByQualityChart from "../components/market/PriceByQualityChart";
import PriceVsSurfaceChart from "../components/market/PriceVsSurfaceChart";
import SeasonalityChart from "../components/market/SeasonalityChart";
import PageContainer from "../components/layout/PageContainer";
import {
  getMarketDashboard,
  getMarketFilters,
} from "../services/api";

const defaultFilters = {
  neighborhood: "",
  houseStyle: "",
  overallQual: "",
  bedroomAbvGr: "",
  fullBath: "",
  saleMonth: "",
  propertyAgeMin: "",
  propertyAgeMax: "",
};

export default function MarketPage() {
  const [filters, setFilters] = useState(defaultFilters);
  const [filterOptions, setFilterOptions] = useState({
    neighborhoods: [],
    house_styles: [],
    overall_qual: [],
    bedroom_abv_gr: [],
    full_bath: [],
    sale_month: [],
    property_age_range: { min: 0, max: 0 },
  });
  const [state, setState] = useState({
    kpis: null,
    byNeighborhood: [],
    priceVsSurface: [],
    byQuality: [],
    priceDistribution: [],
    seasonality: [],
    analysis: null,
  });

  useEffect(() => {
    getMarketFilters().then(setFilterOptions).catch(() => undefined);
  }, []);

  useEffect(() => {
    getMarketDashboard(filters)
      .then((dashboard) => {
        setState({
          kpis: dashboard.kpis,
          byNeighborhood: dashboard.byNeighborhood,
          priceVsSurface: dashboard.priceVsSurface,
          byQuality: dashboard.byQuality,
          priceDistribution: dashboard.priceDistribution,
          seasonality: dashboard.seasonality,
          analysis: dashboard.analysis,
        });
      })
      .catch(() => undefined);
  }, [filters]);

  return (
    <PageContainer
      title="Le marche en chiffres"
      subtitle="Analysez les tendances immobiliere, comparez les segments du marche et interpretez les variations de prix."
    >
      <div className="market-page">
        <MarketFilters filters={filters} setFilters={setFilters} filterOptions={filterOptions} />
        <div className="market-content">
          <KpiCards kpis={state.kpis} />
          <div className="chart-grid">
            <PriceByNeighborhoodChart data={state.byNeighborhood} wide />
            <PriceVsSurfaceChart data={state.priceVsSurface} />
            <PriceByQualityChart data={state.byQuality} />
            <PriceDistributionChart data={state.priceDistribution} />
            <SeasonalityChart data={state.seasonality} wide />
          </div>
          <section className="market-analysis-card">
            <div className="card-header">
              <h3>{state.analysis?.title || "Analyse du marche"}</h3>
              <p>
                {state.analysis?.summary ||
                  "Un resume interpretable du marche apparait ici en fonction des filtres actifs."}
              </p>
            </div>
            <div className="market-analysis-grid">
              {(state.analysis?.highlights || []).map((item) => (
                <article key={item} className="market-analysis-pill">
                  <p>{item}</p>
                </article>
              ))}
            </div>
            {state.analysis?.externalContext ? (
              <div className="market-analysis-external">
                <strong>Contexte externe</strong>
                <p>{state.analysis.externalContext}</p>
              </div>
            ) : null}
          </section>
        </div>
      </div>
    </PageContainer>
  );
}
