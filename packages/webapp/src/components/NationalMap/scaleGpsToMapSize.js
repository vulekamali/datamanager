import { countryGpsBounds, vectorMapSizes } from './data.json';


const [absoluteMinX, absoluteMaxX] = countryGpsBounds.x;
const [absoluteMinY, absoluteMaxY] = countryGpsBounds.y;


const scaleGpsToMapSize = size => (props) => {
  const { 
    x: rawX, 
    y: rawY,
    id,
  } = props || {};

  const maxX = absoluteMaxX - absoluteMinX;
  const maxY = absoluteMaxY - absoluteMinY;

  const x = ((rawX - absoluteMinX) / maxX) * vectorMapSizes[size].x;
  const y = vectorMapSizes[size].y - (((rawY - absoluteMinY) / maxY) * vectorMapSizes[size].y);

  return { x, y, id };
}


export default scaleGpsToMapSize;
