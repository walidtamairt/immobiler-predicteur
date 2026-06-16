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

export default function PredictionForm({ onPredict, error, neighborhoodOptions = [] }) {
  const [form, setForm] = useState(initialForm);

  function submit(event) {
    event.preventDefault();
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
              <select
                value={value}
                onChange={(event) => setForm({ ...form, [key]: event.target.value })}
              >
                {neighborhoodOptions.length ? null : <option value={value}>{value}</option>}
                {neighborhoodOptions.map((option) => (
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
                onChange={(event) => setForm({ ...form, [key]: event.target.value })}
              />
            )}
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
