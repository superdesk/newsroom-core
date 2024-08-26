import React from 'react';
import PropTypes from 'prop-types';
import {shouldRenderLocation, getLocations} from 'maps/utils';
import StaticMap from 'maps/components/static';
import BannerDrop from 'components/BannerDrop';
import {gettext} from '../../utils';

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
            id={item._id}
            labelCollapsed={gettext('Show Map')}
            labelOpened={gettext('Hide Map')}
            isOpenDefault={true}
        >
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
