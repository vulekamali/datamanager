import React, { Component } from 'react';
import findProject from './findProject';
import calcSelected from './calcSelected';
import scaleGpsToMapSize from './scaleGpsToMapSize';
import Markup from './Markup';


class NationalMap extends Component {
  constructor(props) {
    super(props);
    const {
      projects,
      size,
      selected: selectedRaw,
    } = this.props;

    this.state = {
      hover: null,
      // selected: calcSelected(projects)(selectedRaw), 
    }

    this.events = {
      updateHover: this.updateHover.bind(this),
      updateSelected: this.updateSelected.bind(this),
    }

    this.values = {
      // points: pointsRaw.map(scaleGpsToMapSize(size)),
    }
  }

  updateHover(hover) {
    return this.setState({ hover });
  }

  updateSelected(selected) {
    const { projects, selectionCallback } = this.props;

    if (selectionCallback) {
      const project = findProject(projects)(selected);
      selectionCallback({ selected, project });
    }

    return this.setState({ selected });
  }

  render() {
    const { props, values, state, events } = this;

    const passedProps = {
      activeProvinces: props.activeProvinces,
      size: props.size,
      projects: props.projects,
      points: props.points ? props.points.map(scaleGpsToMapSize('large')) : [],
      hover: state.hover,
      selected: state.selected,
      updateSelected: events.updateSelected,
      updateHover: events.updateHover,
    };

    return <Markup {...passedProps} />
  }
}


export default NationalMap;


// NationalMap.propTypes = {
//   /** A function to call when the location selection is changed. First parameter is an object returning the location ID (as 'selected') and the project (as 'project'). */
//   selectionCallback: t.func,
//   /** GPS point to mark as selected when component is initialised */
//   selected: t.number,
//   /** Size at which to create the NationalMap component */
//   size: t.oneOf(['small', 'medium', 'large']).isRequired,
//   /** An array of GPS locations by longitude (x) and latitude (y). Ids (needs to be unique) is used in 'projects' prop to link project to locations. */
//   points: t.arrayOf(t.shape({
//     id: t.string,
//     x: t.number,
//     y: t.number,
//   })),
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
//   }))
// };


// NationalMap.defaultProps = {
//   points: [],
//   projects: [],
//   selected: null,
//   selectionCallback: null,
// }