import React from 'react';
import PropTypes from 'prop-types';
import {gettext} from '../../utils';
import {get} from 'lodash';
import BannerDrop from 'assets/components/BannerDrop';
import StaticMap from 'assets/maps/components/static';
import {shouldRenderLocation, getLocations} from 'assets/maps/utils';

/**
 * Display map image for item location
 * @param {Object} item
 * @param {function} onClick
 */
export default function AgendaPreviewImage({item, onClick}: any) {
    if (!shouldRenderLocation(item)) {
        return null;
    }

    const locations = getLocations(item);

    return (
        <BannerDrop
            id={get(item, '_id')}
            labelCollapsed={gettext('Show Map')}
            labelOpened={gettext('Hide Map')}
            isOpen={get(item, 'coverages.length', 0) === 0} >
            <div className="wire-column__preview__image" onClick={() => onClick(item)}>
                <StaticMap locations={locations} />
            </div>
        </BannerDrop>
    );
}

AgendaPreviewImage.propTypes = {
    item: PropTypes.object.isRequired,
    onClick: PropTypes.func.isRequired,
};
