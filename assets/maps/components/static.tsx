import React from 'react';
import {getMapSource} from '../utils';
import {gettext} from '../../utils';

interface IProps {
    scale?: number;
    locations?: Array<any>;
}

interface IState {
    mapLoaded: boolean;
}

export default class StaticMap extends React.Component<IProps, IState> {
    constructor(props: IProps) {
        super(props);
        this.state = {
            mapLoaded: false
        };
        this.handleMapError = this.handleMapError.bind(this);
        this.handleMapLoaded = this.handleMapLoaded.bind(this);
    }

    handleMapLoaded() {
        this.setState({mapLoaded: true});
    }

    handleMapError() {
        this.setState({mapLoaded: false});
    }

    render() {
        const src = getMapSource(this.props.locations, this.props.scale);

        return (
            <img
                style={this.state.mapLoaded ? {} : {display: 'none'}}
                src={src}
                width="640"
                height="640"
                onLoad={this.handleMapLoaded}
                onError={this.handleMapError}
                alt={gettext('Map')}
            />
        );
    }
}
