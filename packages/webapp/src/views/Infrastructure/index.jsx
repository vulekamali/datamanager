import React, { Component } from 'react';
import Markup from './Markup';


class Infrastructure extends Component {
  constructor(props) {
    super(props);
    const { 
      details: initialDetails,
      projectId,
      projects = [],
    } = this.props;

    const fixedSlugs = projects.map(({ id: rawId, ...other}) => ({
      id: rawId.replace(/^\/infrastructure-projects\//g, ''),
      ...other,
    }))

    this.state = {
      id: !!projectId ? fixedSlugs.findIndex(({ id }) => id === projectId) : 0,
      details: initialDetails || !!projectId || false,
    }

    this.events = {
      nextId: this.nextId.bind(this),
    }
  }

  toggleDetails() {
    const { details } = this.state;
    this.setState({ details: !details })
  }

  nextId(value) {
    const { id, details } = this.state;
    const { projects } = this.props;
    const max = projects.length;

    if (!details) {
      window.history.pushState({}, window.document.title, `/infrastructure-projects?preview=${id}` );
    } else {
      if (value === true && value < max) {
        window.history.pushState({}, window.document.title, projects[id + 1].id);
      }
  
      if (value === false && id > 0) {
        window.history.pushState({}, window.document.title, projects[id - 1].id);
      }
      
    }

    if (value === true && value < max) {
      this.setState({ id: id + 1 })
    }

    if (value === false && id > 0) {
      this.setState({ id: id - 1 });
    }
  }

  render() {
    const { props, state, events } = this;

    const passedProps = {
      id: state.id,
      projects: props.projects || [],
      points: props.points || [],
      nextId: events.nextId,
      details: state.details,
      toggleDetails: events.toggleDetails,
      datasetUrl: props.datasetUrl,
      budgetReviewUrl: props.budgetReviewUrl,
      Link: props.Link,
      chartData: props.chartData,
    }

    return <Markup {...passedProps} />
  }
}

export default Infrastructure;
