import React from 'react';
import PropTypes from 'prop-types';
import CardMeta from './CardMeta';

function CardFooter({wordCount, charCount, pictureAvailable, source, versioncreated, listConfig, item}) {
    return (<div className="card-footer">
        <CardMeta
            item={item}
            pictureAvailable={pictureAvailable}
            wordCount={wordCount}
            charCount={charCount}
            source={source}
            versioncreated={versioncreated}
            listConfig={listConfig}
        />
    </div>);
}

CardFooter.propTypes = {
    item: PropTypes.object.isRequired,
    wordCount: PropTypes.number,
    charCount: PropTypes.number,
    pictureAvailable: PropTypes.bool,
    source: PropTypes.string,
    versioncreated: PropTypes.string,
    listConfig: PropTypes.object,
};

export default CardFooter;
