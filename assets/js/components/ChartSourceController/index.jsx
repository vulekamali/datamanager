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

        const {initial, items, type, inYearEnabled, departmentName} = this.props;
        const source = initial || Object.keys(items)[0];

        const barItems = this.getBarItems(this.props.items, source, type);
        this.state = {
            source: source,
            barItems: barItems,
            barTypes: this.props.barTypes
        };
        const sphere = document.getElementById('sphere-slug').value;

        if (type == "expenditurePhase" && inYearEnabled && sphere == "national")
          this.fetchActualExpenditureUrls(departmentName);

        this.events = {
            changeSource: this.changeSource.bind(this),
        };
    }

    getBarItems(barItems, source, type) {
        if (type !== 'expenditurePhase') {
            return barItems[source];
        }

        Object.keys(barItems).forEach((sourceType) => {
            let tempItems = barItems[sourceType];
            Object.keys(tempItems).forEach((key) => {
                for (let i = 0; i < 4; i++) {
                    // each quarter is null initially
                    tempItems[key].push(null);
                }
            })
        })

        return barItems[source];
    }

    fetchActualExpenditureUrls(departmentName) {
        let selectedYear = document.querySelector('#selected-year').value;
        let url = `../../actual-expenditure/?department_name=${encodeURI(departmentName)}&selected_year=${selectedYear}`;
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
        if (url == null){
            return
        }
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
        this.setState({
            source,
            barItems: this.props.items[source]
        });
    }

    getToggle(toggle, type) {
        if (type !== 'expenditurePhase') {
            return toggle;
        }
        const extraText = ' Actual expenditure is not currently available on the inflation-adjusted view';
        if (toggle['real']['description'].indexOf(extraText) >= 0) {
            return toggle;
        }
        toggle['real']['description'] += extraText

        return toggle;
    }

    render() {
        const {styling, downloadText} = this.props;
        const {source} = this.state;
        const {changeSource} = this.events;
        let toggle = this.getToggle(this.props.toggle, this.props.type);

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
