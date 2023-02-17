import ReactDOM from "react-dom";
import React, {Component} from "react";
import {Button, Card, CardContent, CardMedia, Grid, makeStyles} from "@material-ui/core";
import ForwardArrow from "@material-ui/icons/ArrowForward";

class Showcase extends Component {
    constructor(props) {
        super(props);

        this.state = {
            features: [{
                image: '/static/media/construction-workers.7acfdeab.jpg',
                title: 'Card title',
                description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur rutrum lacinia varius. Proin vitae pulvinar libero',
                buttonText: 'Green button',
                buttonText2: 'Learn more about something'
            }, {
                image: '/static/media/construction-workers.7acfdeab.jpg',
                title: 'Card title',
                description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur rutrum lacinia varius. Proin vitae pulvinar libero',
                buttonText: 'Green button',
                buttonText2: 'Learn more about something'
            }, {
                image: '/static/media/construction-workers.7acfdeab.jpg',
                title: 'Card title',
                description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur rutrum lacinia varius. Proin vitae pulvinar libero',
                buttonText: 'Green button',
                buttonText2: 'Learn more about something'
            }, {
                image: '/static/media/construction-workers.7acfdeab.jpg',
                title: 'Card title',
                description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur rutrum lacinia varius. Proin vitae pulvinar libero',
                buttonText: 'Green button',
                buttonText2: 'Learn more about something'
            }, {
                image: '/static/media/construction-workers.7acfdeab.jpg',
                title: 'Card title',
                description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur rutrum lacinia varius. Proin vitae pulvinar libero',
                buttonText: 'Green button',
                buttonText2: 'Learn more about something'
            }]
        }
    }

    render() {
        return (<Grid
            style={{maxWidth: '1300px', margin: 'auto'}}
            container
            spacing={3}
        >
            {this.state.features.map(feature => {
                return (<Grid item xs={6}>
                    <Card
                        style={{display: 'flex'}}
                    >
                        <CardMedia
                            image={feature.image}
                            style={{minWidth: '220px', height: '0', paddingTop: '31%'}}
                        />
                        <CardContent>
                            <b>{feature.title}</b>
                            <p>{feature.description}</p>
                            <a
                                href={'#'}
                                style={{
                                    backgroundColor: '#70b352',
                                    color: '#fff',
                                    width: '100%',
                                    textDecoration: 'none',
                                    display: 'block',
                                    padding: '6px 16px',
                                    borderRadius: '4px',
                                    fontWeight: '700',
                                    marginBottom: '12px'
                                }}
                            >
                                <Grid container>
                                    <Grid
                                        item xs={9}
                                        style={{height: '25px', lineHeight: '25px'}}
                                    >{feature.buttonText}</Grid>
                                    <Grid
                                        item xs={3}
                                        style={{height: '25px', lineHeight: '25px', textAlign: 'right'}}
                                    >
                                        <ForwardArrow/>
                                    </Grid>
                                </Grid>
                            </a>
                            <a href="#">{feature.buttonText2}</a>
                        </CardContent>
                    </Card>
                </Grid>)
            })}
        </Grid>)
    }
}

function scripts() {
    const parent = document.getElementById('js-initShowcase');
    if (parent) {
        ReactDOM.render(<Showcase/>, parent)
    }
}

export default scripts();