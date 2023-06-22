import React from 'react';
import PropTypes from 'prop-types';
import CardRow from './CardRow';
import CardFooter from './CardFooter';
import {getPicture, shortText} from 'wire/utils';
import {Embargo} from '../../../wire/components/fields/Embargo';

const getTextOnlyPanel = (item, openItem, picture, cardId, listConfig) => (
    <div key={item._id} className='col-sm-6 col-md-4 col-lg-3 col-xxl-2 d-flex mb-4'>
        <div className='card card--home' onClick={() => openItem(item, cardId)}>
            <div className='card-body'>
                <h4 className='card-title'>{item.headline}</h4>
                <Embargo item={item} isCard={true} />
                <div className='wire-articles__item__text'>
                    <p className='card-text small'>{shortText(item, 40, listConfig)}</p>
                </div>
            </div>
            <CardFooter
                item={item}
                picture={picture}
                listConfig={listConfig}
            />
        </div>
    </div>
);


function TextOnlyCard ({items, title, productId, openItem, isActive, cardId, listConfig}) {
    return (
        <CardRow title={title} productId={productId} isActive={isActive}>
            {items.map((item) => getTextOnlyPanel(item, openItem, getPicture(item), cardId, listConfig))}
        </CardRow>
    );
}

TextOnlyCard.propTypes = {
    items: PropTypes.array,
    title: PropTypes.string,
    productId: PropTypes.string,
    openItem: PropTypes.func,
    isActive: PropTypes.bool,
    cardId: PropTypes.string,
    listConfig: PropTypes.object,
};

export default TextOnlyCard;
