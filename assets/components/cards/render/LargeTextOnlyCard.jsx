import React from 'react';
import PropTypes from 'prop-types';
import {characterCount, wordCount} from 'utils';
import CardFooter from './CardFooter';
import CardBody from './CardBody';
import CardRow from './CardRow';
import {getPicture} from 'wire/utils';

const getTextOnlyPanel = (item, openItem, cardId, listConfig) => (
    <div key={item._id} className='col-sm-6 col-lg-4 d-flex mb-4'>
        <div className='card card--home' onClick={() => openItem(item, cardId)}>
            <CardBody item={item} displaySource={false} />
            <CardFooter
                item={item}
                wordCount={wordCount(item)}
                charCount={characterCount(item)}
                pictureAvailable={!!getPicture(item)}
                source={item.source}
                versioncreated={item.versioncreated}
                listConfig={listConfig}
            />
        </div>
    </div>
);

function LargeTextOnlyCard ({items, title, product, openItem, isActive, cardId, listConfig}) {
    return (
        <CardRow title={title} product={product} isActive={isActive}>
            {items.map((item) => getTextOnlyPanel(item, openItem, cardId, listConfig))}
        </CardRow>
    );
}

LargeTextOnlyCard.propTypes = {
    items: PropTypes.array,
    title: PropTypes.string,
    product: PropTypes.object,
    openItem: PropTypes.func,
    isActive: PropTypes.bool,
    cardId: PropTypes.string,
    listConfig: PropTypes.object,
};

export default LargeTextOnlyCard;
