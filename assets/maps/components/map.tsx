import React from 'react';
import PropTypes from 'prop-types';
import {getBounds, getLatLng, mapsLoaded} from '../utils';

let _map: any;

const getMapElement: any = () => document.getElementById('google-map');

const getMap = () => {
    if (!_map) {
        _map = new window.google.maps.Map(getMapElement(), {center: {lat: 0, lng: 0}, zoom: 8});
    }

    return _map;
};

export default class Map extends React.PureComponent<any, any> {
    static propTypes: any;
    markers: never[];
    elem: any;
    constructor(props: any) {
        super(props);

        this.markers = [];
    }

    componentDidMount() {
        if (!mapsLoaded()) {
            return;
        }

        // add map to component
        this.elem.appendChild(getMapElement());
        getMapElement().style.display = 'block';
        getMapElement().style.height = '100%';

        // add markers
        this.markers = this.props.locations.map((location: any) => {
            const bounds = getBounds(location);
            const position = getLatLng(location);

            if (bounds) { // use bounds to center/zoom
                getMap().fitBounds(bounds);
            } else { // fallback to position
                getMap().panTo(position);
            }

            return new window.google.maps.Marker({position: position, map: getMap()});
        });
    }

    componentWillUnmount() {
        // remove map
        getMapElement().style.display = 'none';
        document.body.appendChild(getMapElement());

        // remove markers
        this.markers.forEach((marker: any) => marker.setMap(null));
        this.markers = [];
    }

    render() {
        if (!mapsLoaded()) {
            return null;
        }

        return (
            <div ref={(elem: any) => this.elem = elem} style={{height: 300}} />
        );
    }
}

Map.propTypes = {
    locations: PropTypes.arrayOf(PropTypes.object),
};