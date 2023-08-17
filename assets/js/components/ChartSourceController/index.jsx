import React from 'react';
import uuid from 'uuid/v4';
import BarChart from './components/BarChart/index.jsx';
import fetchWrapper from '../../utilities/js/helpers/fetchWrapper';


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

        const {initial, items, type} = this.props;
        const source = initial || Object.keys(items)[0];

        const barItems = this.getBarItems(this.props.items[source], type);
        console.log({props})
        this.state = {
            source: source,
            barItems: barItems,
            barTypes: this.props.barTypes
        };
        this.fetchActualExpenditureUrls(type);

        this.events = {
            changeSource: this.changeSource.bind(this),
        };
    }

    getBarItems(barItems, type) {
        let tempItems = barItems;
        if (type !== 'expenditurePhase') {
            return tempItems;
        }

        Object.keys(tempItems).forEach((key) => {
            for (let i = 0; i < 4; i++) {
                // each quarter is null initially
                tempItems[key].push(null);
            }
        })

        return tempItems;
    }

    fetchActualExpenditureUrls(type) {
        if (type !== 'expenditurePhase') {
            return;
        }

        const department_name = document.querySelector('h1.Page-mainHeading').innerText;
        let url = `../../actual-expenditure/?department_name=${encodeURI(department_name)}`;
        fetchWrapper(url)
            .then((response) => {
                for (const year in response) {
                    this.fetchAndSetActualExpenditure(year, response[year]);
                }
            })
            .catch((err) => console.warn(err));
    }

    fetchAndSetActualExpenditure(year, obj) {
        let url = obj.url;
        const multiplier = 1000;
        fetchWrapper(url)
            .then((response) => {
                let barItems = this.state.barItems;
                //one for each quarter
                barItems[year][4] = response.summary['q1.sum'] > 0 ? response.summary['q1.sum'] * multiplier : null;    //q1
                barItems[year][5] = response.summary['q2.sum'] > 0 ? response.summary['q2.sum'] * multiplier : null;    //q2
                barItems[year][6] = response.summary['q3.sum'] > 0 ? response.summary['q3.sum'] * multiplier : null;    //q3
                barItems[year][7] = response.summary['q4.sum'] > 0 ? response.summary['q4.sum'] * multiplier : null;    //q4

                this.setState({
                    ...this.state,
                    barItems: barItems
                })
            })
            .catch((err) => console.warn(err));
    }

    changeSource(source) {
        this.setState({source});
    }

    render() {
        const {items: rawItems, toggle, styling, downloadText} = this.props;
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
            'barTypes': this.state.barTypes
        }} />;
    }
}


export default ChartSourceController;
