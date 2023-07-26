import React from 'react';
import uuid from 'uuid/v4';
import BarChart from './components/BarChart/index.jsx';


const buildToggle = ({toggle, changeSource, source}) => {
    const id = uuid();

    const toggleItems = Object.keys(toggle).map((key) => {
        const {title} = toggle[key];
        const htmlId = uuid();

        return (
            <label htmlFor={htmlId} {...{key}} className="ChartSourceController-item">
                <input
                    type="radio"
                    value={key}
                    id={htmlId}
                    name={id}
                    checked={key === source}
                    onChange={event => changeSource(event.target.value)}
                />
                <span className="ChartSourceController-text">{title}</span>
            </label>
        );
    });

    const {description} = toggle[source];

    return (
        <div>
            <div className="ChartSourceController-options">
                {toggleItems}
            </div>
            <p className="ChartSourceController-description">{description}</p>
        </div>
    );
};


const Markup = ({items, toggle, styling, changeSource, source, downloadText, barTypes}) => {
    const {scale, color, rotated} = styling;
    return (
        <div className="ChartSourceController">
            <BarChart {...{barTypes, scale, color, rotated, items, downloadText, source}} />
            {toggle && buildToggle({source, toggle, changeSource})}
        </div>
    );
};


class ChartSourceController extends React.Component {
    constructor(...props) {
        super(...props);

        console.log({'props':this.props})

        const {initial, items} = this.props;
        const source = initial || Object.keys(items)[0];

        this.state = {
            source: source,
            barItems: this.props.items[source]
        };

        this.events = {
            changeSource: this.changeSource.bind(this),
        };
    }

    changeSource(source) {
        this.setState({source});
    }

    render() {
        const {items: rawItems, toggle, styling, downloadText, barTypes} = this.props;
        const {source} = this.state;
        const {changeSource} = this.events;
        const items = rawItems[source];

        return <Markup {...{
            'items': this.state.barItems,
            toggle,
            styling,
            source,
            changeSource,
            downloadText,
            barTypes
        }} />;
    }
}


export default ChartSourceController;
