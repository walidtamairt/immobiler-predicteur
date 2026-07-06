import { useState } from "react";
import SectionTitle from "../common/SectionTitle";
import { fieldLabel, fieldPlaceholder } from "../../utils/display";

const initialForm = {
  GrLivArea: 1500,
  LotArea: 8000,
  OverallQual: 7,
  OverallCond: 5,
  BedroomAbvGr: 3,
  FullBath: 2,
  GarageCars: 2,
  GarageArea: 400,
  Neighborhood: "CollgCr",
  HouseStyle: "1Story",
  MoSold: 6,
  property_age: 10,
};

const NUMERIC_LIMITS = {
  GrLivArea: { min: 334, max: 2978, step: 1 },
  LotArea: { min: 1300, max: 50271, step: 1 },
  OverallQual: { min: 1, max: 10, step: 1 },
  OverallCond: { min: 1, max: 9, step: 1 },
  BedroomAbvGr: { min: 0, max: 6, step: 1 },
  FullBath: { min: 0, max: 3, step: 1 },
  GarageCars: { min: 0, max: 4, step: 1 },
  GarageArea: { min: 0, max: 1390, step: 1 },
  MoSold: { min: 1, max: 12, step: 1 },
  property_age: { min: 0, max: 138, step: 1 },
};

const HOUSE_STYLE_OPTIONS = [
  "1Story",
  "1.5Fin",
  "1.5Unf",
  "2Story",
  "2.5Fin",
  "2.5Unf",
  "SFoyer",
  "SLvl",
];

export default function PredictionForm({ onPredict, error, neighborhoodOptions = [] }) {
  const [form, setForm] = useState(initialForm);
  const [fieldErrors, setFieldErrors] = useState({});

  function validateField(key, value) {
    if (key === "Neighborhood") {
      return value ? "" : "Veuillez choisir un quartier.";
    }

    if (key === "HouseStyle") {
      return value ? "" : "Veuillez choisir un type de maison.";
    }

    const limits = NUMERIC_LIMITS[key];
    const numericValue = Number(value);
    if (Number.isNaN(numericValue)) {
      return "Veuillez entrer une valeur numerique.";
    }
    if (numericValue < limits.min || numericValue > limits.max) {
      return `La valeur doit etre comprise entre ${limits.min} et ${limits.max}.`;
    }
    return "";
  }

  function handleChange(key, value) {
    setForm((current) => ({ ...current, [key]: value }));
    setFieldErrors((current) => ({ ...current, [key]: validateField(key, value) }));
  }

  function submit(event) {
    event.preventDefault();
    const nextErrors = Object.fromEntries(
      Object.entries(form).map(([key, value]) => [key, validateField(key, value)]),
    );
    setFieldErrors(nextErrors);
    if (Object.values(nextErrors).some(Boolean)) {
      return;
    }
    onPredict({
      ...form,
      GrLivArea: Number(form.GrLivArea),
      LotArea: Number(form.LotArea),
      OverallQual: Number(form.OverallQual),
      OverallCond: Number(form.OverallCond),
      BedroomAbvGr: Number(form.BedroomAbvGr),
      FullBath: Number(form.FullBath),
      GarageCars: Number(form.GarageCars),
      GarageArea: Number(form.GarageArea),
      MoSold: Number(form.MoSold),
      property_age: Number(form.property_age),
    });
  }

  return (
    <form className="chart-card prediction-form-card" onSubmit={submit}>
      <SectionTitle
        eyebrow="Formulaire"
        title="Estimer un bien"
        subtitle="Renseignez les caracteristiques du bien pour obtenir une estimation claire et contextualisee."
      />
      <div className="prediction-form-grid">
        {Object.entries(form).map(([key, value]) => (
          <label key={key} className="form-field">
            <span>{fieldLabel(key)}</span>
            {key === "Neighborhood" ? (
              <select value={value} onChange={(event) => handleChange(key, event.target.value)}>
                {neighborhoodOptions.length ? null : <option value={value}>{value}</option>}
                {neighborhoodOptions.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            ) : key === "HouseStyle" ? (
              <select value={value} onChange={(event) => handleChange(key, event.target.value)}>
                {HOUSE_STYLE_OPTIONS.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            ) : (
              <input
                type={isNumericField(key) ? "number" : "text"}
                placeholder={fieldPlaceholder(key)}
                value={value}
                min={NUMERIC_LIMITS[key]?.min}
                max={NUMERIC_LIMITS[key]?.max}
                step={NUMERIC_LIMITS[key]?.step}
                onChange={(event) => handleChange(key, event.target.value)}
              />
            )}
            {fieldErrors[key] ? <small className="field-error">{fieldErrors[key]}</small> : null}
          </label>
        ))}
      </div>
      <button className="primary-button prediction-submit" type="submit">Estimer le prix</button>
      {error ? <p className="error">{error}</p> : null}
    </form>
  );
}

function isNumericField(key) {
  return !["Neighborhood", "HouseStyle"].includes(key);
}
