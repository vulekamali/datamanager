import ReactDOM from "react-dom";
import React, {Component} from "react";
import {Paper} from "@material-ui/core";

class PerformanceIndicators extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <div className="IntroSection-text">
                <Paper
                    className="IntroSection-content"
                    style={{
                        fontSize: '16px',
                        lineHeight: '18px'
                    }}>


                    <div className={`IntroSection-text is-initialised`}>
                        <div
                            className="IntroSection-content"
                        />
                        <div>
                            <div className="IntroSection-fade"/>
                            <div className="IntroSection-button">
                                <button className="Button is-secondary is-inline">Read More</button>
                            </div>


                            <p>
                                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed dignissim venenatis
                                fermentum.
                                Quisque
                                a nunc feugiat, hendrerit leo at, tristique erat. Interdum et malesuada fames ac ante
                                ipsum
                                primis
                                in faucibus. Aenean at mauris quis odio scelerisque vehicula quis dignissim odio. Duis
                                egestas
                                varius massa et finibus. Donec in arcu et purus congue porttitor et id dui. Sed enim
                                urna,
                                ornare
                                quis urna a, facilisis viverra ligula. Etiam imperdiet elit neque, sed tempor dolor
                                interdum
                                nec.
                            </p>
                            <p>
                                Nam diam eros, luctus eu purus eu, finibus eleifend dolor. Nam sit amet ligula ut neque
                                auctor
                                imperdiet. Etiam aliquam leo vel est hendrerit, eu consectetur lectus finibus. Nullam
                                sollicitudin
                                sed felis eu lacinia. Vivamus eu libero finibus, mollis nisi a, blandit lectus. Nunc ac
                                interdum
                                sapien. Mauris egestas, urna ultrices faucibus ornare, massa ante fringilla nisl, at
                                tincidunt
                                enim
                                diam vel purus.
                            </p>
                            <p>
                                Ut iaculis, elit id ornare consectetur, purus eros semper mauris, a tristique dolor eros
                                vel
                                sapien.
                                Nullam in posuere metus. Praesent at laoreet lectus, ut blandit dui. Vivamus elementum
                                libero
                                turpis, vitae iaculis nulla semper nec. Mauris in malesuada nisl, eget scelerisque ex.
                                Pellentesque
                                nec mauris mollis, finibus purus et, sollicitudin quam. Nulla eu nibh eros. Quisque
                                vehicula
                                eleifend dolor at convallis. Proin aliquam varius consectetur. Morbi vel sem sodales,
                                condimentum
                                nulla congue, mattis lorem. Orci varius natoque penatibus et magnis dis parturient
                                montes,
                                nascetur
                                ridiculus mus.
                            </p>
                            <p>
                                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed dignissim venenatis
                                fermentum.
                                Quisque
                                a nunc feugiat, hendrerit leo at, tristique erat. Interdum et malesuada fames ac ante
                                ipsum
                                primis
                                in faucibus. Aenean at mauris quis odio scelerisque vehicula quis dignissim odio. Duis
                                egestas
                                varius massa et finibus. Donec in arcu et purus congue porttitor et id dui. Sed enim
                                urna,
                                ornare
                                quis urna a, facilisis viverra ligula. Etiam imperdiet elit neque, sed tempor dolor
                                interdum
                                nec.
                            </p>
                            <p>
                                Nam diam eros, luctus eu purus eu, finibus eleifend dolor. Nam sit amet ligula ut neque
                                auctor
                                imperdiet. Etiam aliquam leo vel est hendrerit, eu consectetur lectus finibus. Nullam
                                sollicitudin
                                sed felis eu lacinia. Vivamus eu libero finibus, mollis nisi a, blandit lectus. Nunc ac
                                interdum
                                sapien. Mauris egestas, urna ultrices faucibus ornare, massa ante fringilla nisl, at
                                tincidunt
                                enim
                                diam vel purus.
                            </p>
                            <p>
                                Ut iaculis, elit id ornare consectetur, purus eros semper mauris, a tristique dolor eros
                                vel
                                sapien.
                                Nullam in posuere metus. Praesent at laoreet lectus, ut blandit dui. Vivamus elementum
                                libero
                                turpis, vitae iaculis nulla semper nec. Mauris in malesuada nisl, eget scelerisque ex.
                                Pellentesque
                                nec mauris mollis, finibus purus et, sollicitudin quam. Nulla eu nibh eros. Quisque
                                vehicula
                                eleifend dolor at convallis. Proin aliquam varius consectetur. Morbi vel sem sodales,
                                condimentum
                                nulla congue, mattis lorem. Orci varius natoque penatibus et magnis dis parturient
                                montes,
                                nascetur
                                ridiculus mus.
                            </p>
                        </div>
                    </div>


                </Paper>
            </div>
        );
    }
}

class PerformanceIndicatorsContainer extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <div>
                <h3 className="Title Title--section">Indicators of performance</h3>
                <PerformanceIndicators/>
            </div>
        );
    }
}

function scripts() {
    const parent = document.getElementById('js-initPerformanceIndicators');
    if (parent) {
        ReactDOM.render(<PerformanceIndicatorsContainer
        />, parent)
    }
}


export default scripts();