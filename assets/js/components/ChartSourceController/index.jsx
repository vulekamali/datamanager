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
        
        let tempObj = this.props.items[source];
            tempObj['2016-17'].push(null);
            tempObj['2017-18'].push(null);
            tempObj['2018-19'].push(null);
            tempObj['2019-20'].push(null); 

        this.state = {
            source: source,
            barItems: tempObj
        };
            
        this.fetchAndSetActualExpenditure(type);

        this.events = {
            changeSource: this.changeSource.bind(this),
        };
    }

    fetchAndSetActualExpenditure(type) {
    	if(type !== 'expenditurePhase'){
    	    return;
    	}
    
	 let url = '../../actual-expenditure/';
	 fetchWrapper(url)
	 	.then((response) => {
	 		let tempObj = this.state.barItems;
	 		tempObj['2019-20'][4] = response['value'];
	 		this.setState({
	 			...this.state,
	 			barItems: tempObj
	 		});
	 	})
	 	.catch((err) => console.warn(err));
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
