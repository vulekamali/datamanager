import {Component, render, h} from "preact";

class TableContainer extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        return <div>test</div>
    }
}

function scripts() {
    const parent = document.getElementsByClassName('js-initTabularView')[0];

    render(
        <TableContainer/>,
        parent
    );
}


export default scripts();