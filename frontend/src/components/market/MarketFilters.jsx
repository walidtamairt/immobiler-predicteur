import { useEffect, useState } from "react";
import { formatFilterLabel, formatHouseStyle, formatMonth } from "../../utils/display";

const emptyValue = "";
const resetFilters = {
  neighborhood: "",
  houseStyle: "",
  overallQual: "",
  bedroomAbvGr: "",
  fullBath: "",
  saleMonth: "",
  propertyAgeMin: "",
  propertyAgeMax: "",
};

function FilterSelect({ label, value, onChange, options }) {
  return (
    <label className="filter-field">
      <span>{label}</span>
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        <option value={emptyValue}>Tous</option>
        {options.map((option) => (
          <option key={option} value={option}>
            {formatOptionLabel(label, option)}
          </option>
        ))}
      </select>
    </label>
  );
}

export default function MarketFilters({ filters, setFilters, filterOptions }) {
  const [draft, setDraft] = useState(filters);

  useEffect(() => {
    setDraft(filters);
  }, [filters]);

  function updateFilter(key, value) {
    setDraft((current) => ({ ...current, [key]: value }));
  }

  return (
    <section className="filters-panel">
      <div className="card-header">
        <h3>Filter bar</h3>
        <p>Filtrez les dashboards avec un jeu unique de criteres, puis appliquez ou reinitialisez la vue.</p>
      </div>
      <div className="filters-grid">
        <FilterSelect
          label={formatFilterLabel("neighborhood")}
          value={draft.neighborhood}
          onChange={(value) => updateFilter("neighborhood", value)}
          options={filterOptions.neighborhoods || []}
        />
        <FilterSelect
          label={formatFilterLabel("houseStyle")}
          value={draft.houseStyle}
          onChange={(value) => updateFilter("houseStyle", value)}
          options={filterOptions.house_styles || []}
        />
        <FilterSelect
          label={formatFilterLabel("overallQual")}
          value={draft.overallQual}
          onChange={(value) => updateFilter("overallQual", value)}
          options={filterOptions.overall_qual || []}
        />
        <FilterSelect
          label={formatFilterLabel("bedroomAbvGr")}
          value={draft.bedroomAbvGr}
          onChange={(value) => updateFilter("bedroomAbvGr", value)}
          options={filterOptions.bedroom_abv_gr || []}
        />
        <FilterSelect
          label={formatFilterLabel("fullBath")}
          value={draft.fullBath}
          onChange={(value) => updateFilter("fullBath", value)}
          options={filterOptions.full_bath || []}
        />
        <FilterSelect
          label={formatFilterLabel("saleMonth")}
          value={draft.saleMonth}
          onChange={(value) => updateFilter("saleMonth", value)}
          options={filterOptions.sale_month || []}
        />
        <label className="filter-field">
          <span>{formatFilterLabel("propertyAgeMin")}</span>
          <input
            type="number"
            value={draft.propertyAgeMin}
            min={filterOptions.property_age_range?.min ?? 0}
            max={filterOptions.property_age_range?.max ?? 0}
            onChange={(event) => updateFilter("propertyAgeMin", event.target.value)}
          />
        </label>
        <label className="filter-field">
          <span>{formatFilterLabel("propertyAgeMax")}</span>
          <input
            type="number"
            value={draft.propertyAgeMax}
            min={filterOptions.property_age_range?.min ?? 0}
            max={filterOptions.property_age_range?.max ?? 0}
            onChange={(event) => updateFilter("propertyAgeMax", event.target.value)}
          />
        </label>
      </div>
      <div className="filters-actions">
        <button className="primary-button" type="button" onClick={() => setFilters(draft)}>
          Appliquer
        </button>
        <button
          className="ghost-button"
          type="button"
          onClick={() => {
            setDraft(resetFilters);
            setFilters(resetFilters);
          }}
        >
          Reinitialiser
        </button>
      </div>
    </section>
  );
}

function formatOptionLabel(label, option) {
  if (label === formatFilterLabel("houseStyle")) {
    return formatHouseStyle(option);
  }

  if (label === formatFilterLabel("saleMonth")) {
    return formatMonth(option);
  }

  return option;
}
