import React from 'react';
import PropTypes from 'prop-types';
import {getEmbargo, gettext, fullDate} from '../../utils';
import {Label} from 'components/Label';

export default function ArticleEmbargoed({item}: any) {
    const embargo = getEmbargo(item);

    if (!embargo) {
        return null;
    }

    return (
        <Label text={gettext('Embargo: {{ date }}', {date: fullDate(embargo)})} type='alert' style='translucent' className='mb-3' size='big' />
    );
}

ArticleEmbargoed.propTypes = {
    item: PropTypes.shape({
        embargoed: PropTypes.string,
    }),
};
