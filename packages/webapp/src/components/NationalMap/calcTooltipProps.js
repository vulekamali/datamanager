import getById from './getById';


const calcTooltipProps = ({ points: pointRefs = [], title }, points) => {
  return pointRefs.map(key => ({ ...getById(key, points), title }));
};


export default calcTooltipProps;
