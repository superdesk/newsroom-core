import React from 'react';
import PropTypes from 'prop-types';
import {getPicture} from 'wire/utils';
import {FieldComponents} from './fields';
import WireListItemIcons from './WireListItemIcons';

const DEFAULT_META_FIELDS = [
    'urgency',
    'source',
    ['charcount', 'wordcount'],
    'previous_versions',
];

function PreviewMeta({
    item,
    isItemDetail,
    inputRef,
    displayConfig,
    listConfig,
    filterGroupLabels,
}: any) {
    const picture = getPicture(item);
    const fields = displayConfig.metadata_fields || DEFAULT_META_FIELDS;

    return (
        <div className="wire-articles__item__meta wire-articles__item__meta--boxed">
            <WireListItemIcons
                item={item}
                picture={picture}
            />
            <div className="wire-articles__item__meta-info">
                <FieldComponents
                    config={fields}
                    item={item}
                    fieldProps={{
                        listConfig,
                        isItemDetail,
                        inputRef,
                        filterGroupLabels,
                        alwaysShow: true,
                    }}
                />
            </div>
        </div>
    );
}

PreviewMeta.propTypes = {
    item: PropTypes.object,
    isItemDetail: PropTypes.bool,
    inputRef: PropTypes.string,
    displayConfig: PropTypes.object,
    listConfig: PropTypes.object,
    filterGroupLabels: PropTypes.object,
};

export default PreviewMeta;
