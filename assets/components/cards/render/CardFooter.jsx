import React from 'react';
import PropTypes from 'prop-types';
import CardMeta from './CardMeta';

function CardFooter({item, listConfig}) {
    return (<div className="card-footer">
        <CardMeta
            item={item}
            listConfig={listConfig}
        />
    </div>);
}

CardFooter.propTypes = {
    item: PropTypes.object.isRequired,
    listConfig: PropTypes.object,
};

export default CardFooter;
