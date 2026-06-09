const MONTH_LABELS = {
  1: "Janvier",
  2: "Fevrier",
  3: "Mars",
  4: "Avril",
  5: "Mai",
  6: "Juin",
  7: "Juillet",
  8: "Aout",
  9: "Septembre",
  10: "Octobre",
  11: "Novembre",
  12: "Decembre",
};

const HOUSE_STYLE_LABELS = {
  "1Story": "Maison plain-pied",
  "1.5Fin": "Maison 1,5 niveau amenage",
  "1.5Unf": "Maison 1,5 niveau non amenage",
  "2Story": "Maison a deux etages",
  "2.5Fin": "Maison 2,5 niveaux amenages",
  "2.5Unf": "Maison 2,5 niveaux non amenages",
  "SFoyer": "Maison split foyer",
  "SLvl": "Maison split level",
};

const FIELD_LABELS = {
  GrLivArea: "Surface habitable",
  LotArea: "Surface terrain",
  OverallQual: "Qualite generale",
  OverallCond: "Etat general",
  BedroomAbvGr: "Nombre de chambres",
  FullBath: "Nombre de salles de bain",
  GarageCars: "Places de garage",
  GarageArea: "Surface du garage",
  Neighborhood: "Quartier",
  HouseStyle: "Type de maison",
  MoSold: "Mois de vente",
  property_age: "Age du bien",
};

const FIELD_PLACEHOLDERS = {
  GrLivArea: "Ex. 1500",
  LotArea: "Ex. 8000",
  OverallQual: "Ex. 7",
  OverallCond: "Ex. 5",
  BedroomAbvGr: "Ex. 3",
  FullBath: "Ex. 2",
  GarageCars: "Ex. 2",
  GarageArea: "Ex. 400",
  Neighborhood: "Ex. CollgCr",
  HouseStyle: "Ex. Maison plain-pied",
  MoSold: "Ex. Juin",
  property_age: "Ex. 10",
};

export function formatPrice(value) {
  return `${Math.round(Number(value) || 0).toLocaleString("fr-FR")} EUR`;
}

export function formatSurface(value) {
  return `${Math.round(Number(value) || 0).toLocaleString("fr-FR")} pieds²`;
}

export function formatMonth(value) {
  return MONTH_LABELS[Number(value)] || `${value}`;
}

export function formatHouseStyle(value) {
  return HOUSE_STYLE_LABELS[value] || value || "Non renseigne";
}

export function formatQuality(value) {
  return `Qualite ${value}`;
}

export function fieldLabel(key) {
  return FIELD_LABELS[key] || key;
}

export function fieldPlaceholder(key) {
  return FIELD_PLACEHOLDERS[key] || "";
}

export function formatFilterLabel(key) {
  const labels = {
    neighborhood: "Quartier",
    houseStyle: "Style de maison",
    overallQual: "Niveau de qualite",
    bedroomAbvGr: "Nombre de chambres",
    fullBath: "Nombre de salles de bain",
    saleMonth: "Mois de vente",
    propertyAgeMin: "Age du bien minimum",
    propertyAgeMax: "Age du bien maximum",
  };

  return labels[key] || key;
}
