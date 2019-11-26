export const provinceCode = {
  "Eastern Cape": "EC",
  "Free State": "FS",
  "Gauteng": "GT",
  "KwaZulu-Natal": "KZN",
  "Limpopo": "LIM",
  "Mpumalanga": "MP",
  "North West": "NW",
  "Northern Cape": "NC",
  "Western Cape": "WC"
};

export function createTileLayer() {
  return L.tileLayer('//{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
    maxZoom: 18,
    subdomains: 'abc',
  });
}
