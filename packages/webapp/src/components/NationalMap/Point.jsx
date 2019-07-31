import React from 'react';
import styled from 'styled-components';
import getPinStyling from './getPinStyling';
import findProject from './findProject';


const getshadow = ({ hover, select }) => {
  if (hover && !select) {
    return '0.4'
  }
  return '0'
}


const getTransform = getPinStyling('transform');
const getFill = getPinStyling('fill');
const getStroke = getPinStyling('stroke');


const Pin = styled.circle`
  transform: ${getTransform};
  fill: ${getFill};
  stroke: ${getStroke};
  transition: transform 0.3s;
`;

const HitMap = styled.circle`
  cursor: ${({ selected }) => (selected ? 'default' : 'pointer')};
`

const Shadow = styled.rect`
  opacity: ${getshadow};
`

const Point = (props) => {
  const { 
    x,
    y,
    id,
    hoveredId,
    selectedId,
    updateHover, 
    updateSelected,
    projects = [],
  } = props;

  const currentProjectsFind = findProject(projects)
  const { points: selectedArray = [] } = currentProjectsFind(selectedId) || {};
  const { points: hoverArray = [] } = currentProjectsFind(hoveredId) || {};

  const cx = x;
  const cy = y;
  const hover = hoverArray.find(innerId => innerId === id);
  const selected = selectedArray.find(innerId => innerId === id);

  const mouseEnterWrapper = () => updateHover(id);
  const mouseLeaveWrapper = () => updateHover(null);
  const clickWrapper = () => updateSelected(id);

  return (
    <g>
      <Shadow 
      {...{ hover, selected }}
      x={x - 5} 
      y={y - 3} 
      width="10" 
      height="10"
      filter="url(#shadow)"
    />
      <Pin
        {...{ cx, cy, hover, selected }}
        r="5"
        strokeWidth="3"
        stroke={selected ? 'black' : 'none'}
      />
      <HitMap
        {...{ cx, cy }}
        onClick={clickWrapper}
        onMouseEnter={mouseEnterWrapper}
        onMouseLeave={mouseLeaveWrapper}
        r="15"
        opacity="0"
      /> 
    </g>
  );
}


export default Point;


// Point.propTypes = {
//   id: t.string.isRequired,
//   x: t.number.isRequired,
//   y: t.number.isRequired,
//   hoveredId: t.string,
//   selectedId: t.string,
//   updateHover: t.func.isRequired, 
//   updateSelected: t.func.isRequired,
//   projectPoints: t.arrayOf(t.string),
// };


// Point.defaultProps = {
//   hoveredId: null,
//   selectedId: null,
//   projectPoints: [],
// }


