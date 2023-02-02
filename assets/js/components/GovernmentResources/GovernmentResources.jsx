import React from 'react';

function skeletonResources() {
  return (
    <div className="cards-container">
      <div className="item skeleton Card">
        <div className="title skeleton"></div>
        <div className="format skeleton"></div>
        <span className="Button is-secondary skeleton">
          <span className="label skeleton"></span>
        </span>
      </div>

      <div className="item skeleton Card">
        <div className="title skeleton"></div>
        <div className="format skeleton"></div>
        <span className="Button is-secondary skeleton">
          <span className="label skeleton"></span>
        </span>
      </div>

      <div className="item skeleton Card">
        <div className="title skeleton"></div>
        <div className="format skeleton"></div>
        <span className="Button is-secondary skeleton">
          <span className="label skeleton"></span>
        </span>
      </div>
    </div>
  );
};

function renderResources(resources) {
  return resources.map((resource) => {
    return (
      <div key={resource.id} className="item Card">
        <div className="title">{ resource.name }</div>
        <div className="format">{ resource.format }</div>
        <a className="resource-link" href={ resource.url }>
          <span className="Button is-secondary">
            <span className="label">View</span>
          </span>
        </a>
      </div>
    )
  });
};

function originalBudgetSection(resources) {
  let content;

  if (resources === null) {
    content = (<div className="cards-container">{ skeletonResources() }</div>);
  } else {
    if (resources.length > 0) {
      content = (<div className="cards-container">{ renderResources(resources) }</div>);
    } else {
      content = (<div>Budget documents not available on vulekamali yet.</div>);
    }
  }

  return (
    <div>
      <h4 className="section-heading">Original budget</h4>
      { content }
    </div>
  )
}

function adjustedBudgetSection(resources) {
  if (resources !== null && resources.length > 0) {
    return (
      <div>
        <h4 className="section-heading">Adjusted budget</h4>
        <div className="cards-container">
          { renderResources(resources) }
        </div>
      </div>
    )
  } else { return null }
}

function isCollapsable(resources) {
  if (resources === null)
    return false;
  else
    return resources.length > 3;
}

export default class GovernmentResources extends React.Component {
  constructor(props) {
    super(props);

    this.handleExpandClick = this.handleExpandClick.bind(this);

    this.state = {
      hasExpanded: false,
    };
  }

  render() {
    const govResourceGroups = this.props.govResourceGroups;
    const collapsed = !this.state.hasExpanded && isCollapsable(govResourceGroups.original);
    return (
      <div className={`budget-documents ${collapsed ? "collapsed" : ""}`}>
        <h3>Key budget documents</h3>
        { adjustedBudgetSection(govResourceGroups.adjusted) }
        { originalBudgetSection(govResourceGroups.original) }
        {
          collapsed ? (
            <div className="expand-shim" onClick={this.handleExpandClick} >
              <div className="Button is-secondary">See all</div>
            </div>
          ) : null
        }
      </div>
    );
  }

  handleExpandClick() {
    this.setState({hasExpanded: true});
  }
}
