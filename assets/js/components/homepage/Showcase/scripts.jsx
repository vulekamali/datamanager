import ReactDOM from "react-dom";
import React, {Component} from "react";
import {Card, CardContent, CardMedia, Grid} from "@material-ui/core";
import ForwardArrow from "@material-ui/icons/ArrowForward";

class Showcase extends Component {
    constructor(props) {
        super(props);

        this.state = {
            features: JSON.parse(document.getElementById('page-data').textContent)
        }
    }

    renderCTA(type, text, link) {
        if (type === "primary") {
            return (
                <a
                    href={link}
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
                    target={'_blank'}
                >
                    <Grid container>
                        <Grid
                            item xs={9}
                            style={{height: '25px', lineHeight: '25px'}}
                        >{text}</Grid>
                        <Grid
                            item xs={3}
                            style={{height: '25px', lineHeight: '25px', textAlign: 'right'}}
                        >
                            <ForwardArrow/>
                        </Grid>
                    </Grid>
                </a>
            )
        } else if (type === "secondary") {
            return (
                <a
                    href={link}
                    target={'_blank'}
                >{text}</a>
            )
        }
    }

    render() {
        return (<Grid
            style={{maxWidth: '1300px', margin: 'auto'}}
            container
            spacing={3}
        >
            {this.state.features.map(feature => {
                return (
                    <Grid item xs={6} key={feature.pk}>
                        <Card
                            style={{display: 'flex'}}
                        >
                            <CardMedia
                                image={feature.fields.file}
                                style={{minWidth: '220px', height: '0', paddingTop: '36%'}}
                            />
                            <CardContent>
                                <b>{feature.fields.name}</b>
                                <p>{feature.fields.description}</p>
                                {this.renderCTA('primary', feature.fields.cta_text_1, feature.fields.cta_link_1)}
                                {this.renderCTA(feature.fields.second_cta_type, feature.fields.cta_text_2, feature.fields.cta_link_2)}
                            </CardContent>
                        </Card>
                    </Grid>
                )
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