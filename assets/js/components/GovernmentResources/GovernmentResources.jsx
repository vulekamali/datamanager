import { h, Component, render } from 'preact';

function skeleton() {
  return (
    <div className="budget-documents">
      <h4 className="section-heading">Original budget</h4>

      <div className="item skeleton Card">
        <div className="title skeleton"></div>
        <a className="resource-link skeleton">
          <span className="Button is-secondary skeleton">
            <span className="label skeleton"></span>
          </span>
        </a>
      </div>

      <div className="item skeleton Card">
        <div className="title skeleton"></div>
        <a className="resource-link skeleton">
          <span className="Button is-secondary skeleton">
            <span className="label skeleton"></span>
          </span>
        </a>
      </div>

      <div className="item skeleton Card">
        <div className="title skeleton"></div>
        <a className="resource-link skeleton">
          <span className="Button is-secondary skeleton">
            <span className="label skeleton"></span>
          </span>
        </a>
      </div>
    </div>
  );
};

function renderResources(resources) {
  const cards = resources.original.map((resource) => {
    console.log(resource);
    (
      <div key={resource.id} className="item Card">
        <div className="title">{ resource.title }</div>
        <a className="resource-link" href={ resource.url }>
          <span className="Button is-secondary">
            <span className="label">View</span>
          </span>
        </a>
      </div>
    )
  });
  return (
    <div className="budget-documents">
      <h4 className="section-heading">Original budget</h4>
      { cards }
    </div>
  );
};
export default class GovernmentResources extends Component {
  constructor(props) {
    super(props);

    this.state = {
      loading: false,
    };
  }

  render() {
    const resources = this.props.resources;
    return resources === null ? skeleton() : renderResources(resources);
  }
}
