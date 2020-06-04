import { h, Component, render } from 'preact';

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

export default class GovernmentResources extends Component {
  constructor(props) {
    super(props);

    this.state = {
      loading: false,
    };
  }

  render() {
    const govResourceGroups = this.props.govResourceGroups;
    return (
      <div className="budget-documents">
        <h3>Key budget documents</h3>
        { adjustedBudgetSection(govResourceGroups.adjusted) }
        { originalBudgetSection(govResourceGroups.original) }
      </div>
    );
  }
}
