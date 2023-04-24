import {getSlugline, shortDate} from 'assets/utils';
import {shortText} from 'assets/wire/utils';
import PropTypes from 'prop-types';
import React from 'react';
import {Embargo} from '../../../wire/components/fields/Embargo';

function CardBody({item, displayMeta, displayDescription, displaySource, listConfig}: any): any {
    return (<div className="card-body">
        <h4 className="card-title">{item.headline}</h4>

        <Embargo item={item} isCard={true} />

        {displayDescription && <div className="wire-articles__item__text">
            <p className='card-text small'>{shortText(item, 40, listConfig)}</p>
        </div>}

        {displayMeta && (
            <div className="wire-articles__item__meta">
                <div className="wire-articles__item__meta-info">
                    <span className="bold">{getSlugline(item, true)}</span>
                    {displaySource &&
                    <span>{item.source} {'//'} </span>}
                    <span>{shortDate(item.versioncreated)}</span>
                </div>
            </div>
        )}
    </div>);
}

CardBody.propTypes = {
    item: PropTypes.object,
    displayMeta: PropTypes.bool,
    displayDescription: PropTypes.bool,
    displaySource: PropTypes.bool,
    listConfig: PropTypes.object,
};

CardBody.defaultProps = {
    displayMeta: true,
    displayDescription: true,
    displaySource: true,
};

export default CardBody;
