import React from 'react';
import PropTypes from 'prop-types';
import CardFooter from './CardFooter';
import CardBody from './CardBody';
import CardRow from './CardRow';
import {getPicture} from 'wire/utils';

const getTextOnlyPanel = (item, openItem, cardId, listConfig) => (
    <div key={item._id} className='col-sm-6 col-lg-4 d-flex mb-4'>
        <div className='card card--home' onClick={() => openItem(item, cardId)}>
            <CardBody item={item} displaySource={false} listConfig={listConfig} />
            <CardFooter
                item={item}
                picture={getPicture(item)}
                listConfig={listConfig}
            />
        </div>
    </div>
);

function LargeTextOnlyCard ({items, title, productId, openItem, isActive, cardId, listConfig}) {
    return (
        <CardRow title={title} productId={productId} isActive={isActive}>
            {items.map((item) => getTextOnlyPanel(item, openItem, cardId, listConfig))}
        </CardRow>
    );
}

LargeTextOnlyCard.propTypes = {
    items: PropTypes.array,
    title: PropTypes.string,
    productId: PropTypes.string,
    openItem: PropTypes.func,
    isActive: PropTypes.bool,
    cardId: PropTypes.string,
    listConfig: PropTypes.object,
};

export default LargeTextOnlyCard;
