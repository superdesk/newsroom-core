import React from 'react';
import PropTypes from 'prop-types';
import CardMeta from './CardMeta';

function CardFooter({item, picture, listConfig}) {
    return (<div className="card-footer">
        <CardMeta
            item={item}
            picture={picture}
            listConfig={listConfig}
        />
    </div>);
}

CardFooter.propTypes = {
    item: PropTypes.object.isRequired,
    picture: PropTypes.object,
    listConfig: PropTypes.object,
};

export default CardFooter;
