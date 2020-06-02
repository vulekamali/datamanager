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

export default class GovernmentResources extends Component {
  constructor(props) {
    super(props);

    this.state = {
      loading: false,
    };

    console.log(`constructor ${props.title}`);
  }

  componentDidMount() {
    console.log("componentDidmount");
  }

  render() {
    console.log("render");
    return skeleton();
  }
}
