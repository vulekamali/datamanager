import React from 'react';
import styled from 'styled-components';
import { provincesList, vectorMapSizes } from './data.json';
import findProject from './findProject';
import calcTooltipProps from './calcTooltipProps';
import Province from './Province';
import Point from './Point';
import Tooltip from './Tooltip';


const Wrapper = styled.div`
  position: relative;
  width: ${({ size }) => vectorMapSizes[size].x}px;
  height: ${({ size }) => vectorMapSizes[size].y}px;
`;


const createProvince = (activeProvinces, size) => name => {
  return <Province {...{ name, size, activeProvinces }} key={name} />;
}


const createPoint = (props) => gpsPoint => {
  const {
    projects,
    hover,
    selected,
    updateHover,
    updateSelected,
  } = props;

  const {
    x,
    y,
    id,
  } = gpsPoint || {};

  const pointProps = {
    x,
    y,
    id,
    updateHover,
    updateSelected,
    projects,
    hoveredId: hover,
    selectedId: selected,
  };

  return (
    <Point
      {...pointProps}
      hover
      selected
      key={id}
    />
  )
};


const defineSvgShadowForHover = (
  <defs>
    <filter id="shadow" x="-200%" y="-200%" width="500%" height="500%">
      <feGaussianBlur in="SourceAlpha" stdDeviation="3" />
    </filter>
  </defs>
);


const Markup = (props) => {
  const {
    points = [],
    hover,
    selected,
    size,
    updateSelected,
    updateHover,
    projects = [],
    activeProvinces,
  } = props;

  const createPointArgs = {
    projects,
    hover,
    selected,
    updateHover,
    updateSelected,
  };

  return (
    <Wrapper {...{ size }}>
      <svg
        version="1"
        xmlns="http://www.w3.org/2000/svg"
        width={vectorMapSizes[size].x}
        height={vectorMapSizes[size].y}
        viewBox="0 0 428 375"
      >
        {defineSvgShadowForHover}
        {provincesList.map(createProvince(activeProvinces, size))}
        {points.map(createPoint(createPointArgs))}
      </svg>
      {/* <Tooltip items={calcTooltipProps(hoverProject, points)} /> */}
    </Wrapper>
  )
}


export default Markup;


// Markup.propTypes = {
//   /** An array of GPS locations by longitude (x) and latitude (y). Ids (needs to be unique) is used in 'projects' prop to link project to locations. */
//   points: t.arrayOf(t.shape({
//     id: t.string,
//     x: t.number,
//     y: t.number,
//   })).isRequired,
//   /** An array of infrastructure projects to show on map. Ids need to be unique.  */
//   projects: t.arrayOf(t.shape({
//     id: t.String,
//     title: t.Number,
//     points: t.arrayOf(t.string),
//     provinces: t.arrayOf(t.string),
//     budget: t.shape({
//       projected: t.number,
//       total: t.number,
//     }),
//   })),
//   /** GPS point of currently hovered pin */
//   hover: t.string,
//   /** GPS point of currently selected pin */
//   selected: t.string,
//   /** Size at which to create the NationalMap component */
//   size: t.oneOf(['small', 'medium', 'large']).isRequired,
//   /** Callback function that changes the state of 'selected' */
//   updateSelected: t.func.isRequired,
//   /** Callback function that changes the state of 'hover'. Has side-effects */
//   updateHover: t.func.isRequired,
// };


// Markup.defaultProps = {
//   points: [],
//   projects: [],
//   selected: null,
//   hover: null,
// }
