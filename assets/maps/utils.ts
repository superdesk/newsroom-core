import {get, isEmpty} from 'lodash';
import {getConfig} from '../utils';

const MAPS_URL = 'https://maps.googleapis.com/maps/api/staticmap';

/**
 * Get item locations
 * @param {Object} item
 */
export function getLocations(item: any) {
    return (get(item, 'location')) || [];
}

/**
 * Get locations with geo coordinates
 * @param {Object} item
 * @return {Array}
 */
export function getGeoLocations(locations: any) {
    return locations.filter((loc: any) => get(loc, 'location.lat'));
}

/**
 * Get location address for item
 *
 * @param {Object} item
 * @return {Object}
 */
export function getAddress(item: any) {
    return get(item, 'location.0.address');
}

/**
 * Get location bounding box
 * @param {Object} location
 * @return {Array}
 */
export function getBoundingBox(location: any) {
    return get(location, 'address.boundingbox');
}

/**
 * Get location address line
 * @param {Object} location
 * @return {String}
 */
export function getAddressLine(location: any) {
    return get(location, 'address.line.0');
}

/**
 * Get address state
 *
 * @param {Object} location
 */
export function getAddressState(location: any) {
    return get(location, 'address.state') || get(location, 'address.locality');
}

/**
 * Get address country
 *
 * @param {Object} location
 */
export function getAddressCountry(location: any) {
    return get(location, 'address.country');
}

/**
 * Get bounds for location
 * @param {Object} location
 * @return {LatLngBoundsLiteral}
 */
export function getBounds(location: any) {
    const bbox = getBoundingBox(location);

    if (bbox) {
        return {
            south: parseFloat(bbox[0]),
            north: parseFloat(bbox[1]),
            west: parseFloat(bbox[2]),
            east: parseFloat(bbox[3]),
        };
    }
}

/**
 * Get position for location
 * @param {Object} location
 * @return {LatLngLiteral}
 */
export function getLatLng(location: any) {
    return {
        lat: get(location, 'location.lat'),
        lng: get(location, 'location.lon'),
    };
}

export function mapsLoaded() {
    return window.mapsLoaded;
}

export function mapsKey() {
    return window.googleMapsKey;
}

/**
 * Get zoom param based on location
 * @param {Object} location
 */
function getZoom(location: any) {
    const box = getBoundingBox(location);
    const line = getAddressLine(location);

    if (box) { // use bounding box if provided
        return [
            {lat: box[0], lon: box[2]},
            {lat: box[1], lon: box[3]},
        ].map((point: any) => 'visible=' + encodeURIComponent(point.lat + ',' + point.lon)).join('&');
    }

    // fallback to zoom, use 15 if we are on street level, 8 otherwise
    return !isEmpty(line) ? 'zoom=15' : 'zoom=8';
}

function getLocationDetails(location: any) {
    return [location.name,
        getAddressLine(location),
        getAddressState(location),
        getAddressCountry(location),
    ].filter((x: any) => !!x).join(', ');
}

export function getMapSource(locations: any, scale: any = 1) {
    if (isEmpty(locations)) {
        return '';
    }

    let params = [
        'size=600x306',
        'key=' + mapsKey(),
        'scale=' + scale
    ];

    const google_maps_styles = getConfig('google_maps_styles');

    if (google_maps_styles) {
        const styles = google_maps_styles.split('&').filter((s: any) => s).map((s: any) => `style=${s}`);
        if (get(styles, 'length', 0) > 0) {
            params = params.concat(styles);
        }
    }

    const geoLocations = getGeoLocations(locations);
    let src: any;

    if (!isEmpty(geoLocations)) {
        const markers = geoLocations.map((loc: any) => 'markers=' + encodeURIComponent(loc.location.lat + ',' + loc.location.lon));
        params.push(getZoom(geoLocations[0]));
        src = MAPS_URL + '?' + markers.concat(params).join('&');
    } else {
        const location = locations[0];
        params.push('center=' + encodeURIComponent(getLocationDetails(location)));
        params.push('markers=' + encodeURIComponent(getLocationDetails(location)));
        src = MAPS_URL + '?' + params.join('&');
    }

    return src;
}

export function shouldRenderLocation(item: any) {
    return !isEmpty(mapsKey()) && !isEmpty(getLocations(item));
}
