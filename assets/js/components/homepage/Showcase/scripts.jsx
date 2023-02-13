import ReactDOM from "react-dom";
import React, {Component} from "react";
import {Button, Card, CardContent, CardMedia, Grid, IconButton} from "@material-ui/core";
import ForwardArrow from "@material-ui/icons/ArrowForward";

class Showcase extends Component {
    constructor(props) {
        super(props);

        this.state = {
            features: [{
                image: '/static/media/construction-workers.7acfdeab.jpg',
                title: 'Card title',
                description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur rutrum lacinia varius. Proin vitae pulvinar libero',
                buttonText: 'Green button'
            }, {
                image: '/static/media/construction-workers.7acfdeab.jpg',
                title: 'Card title',
                description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur rutrum lacinia varius. Proin vitae pulvinar libero',
                buttonText: 'Green button'
            }, {
                image: '/static/media/construction-workers.7acfdeab.jpg',
                title: 'Card title',
                description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur rutrum lacinia varius. Proin vitae pulvinar libero',
                buttonText: 'Green button'
            }, {
                image: '/static/media/construction-workers.7acfdeab.jpg',
                title: 'Card title',
                description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur rutrum lacinia varius. Proin vitae pulvinar libero',
                buttonText: 'Green button'
            }, {
                image: '/static/media/construction-workers.7acfdeab.jpg',
                title: 'Card title',
                description: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur rutrum lacinia varius. Proin vitae pulvinar libero',
                buttonText: 'Green button'
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
                                    style={{minWidth: '200px', height: '0', paddingTop: '24%'}}
                                />
                                <CardContent>
                                    <b>{feature.title}</b>
                                    <p>{feature.description}</p>
                                    <Button
                                        endIcon={<ForwardArrow/>}
                                        style={{backgroundColor:'#70b352'}}
                                    >
                                        {feature.buttonText}
                                    </Button>
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