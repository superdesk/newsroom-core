import * as React from 'react';
import PropTypes from 'prop-types';
import InfoBox from '../InfoBox';
import {gettext} from 'assets/utils';

export function Authors({item}: any) {
    if (!item || !item.authors || !item.authors.length) {
        return null;
    }

    return (
        <InfoBox label={gettext('Authors')}>
            {item.authors.map((author: any) => (
                <div key={author.code + '/' + author.role} className="wire-column__preview__item__author">
                    <h5>{author.role}</h5>
                    <h6>{author.name}</h6>
                    {(!author.biography || !author.biography.length) ? null : (
                        <p>{author.biography.split('\n').map((item: any, key: any) => (
                            <span key={key}>{item}<br/></span>
                        ))}</p>
                    )}
                </div>
            ))}
        </InfoBox>
    );
}

Authors.propTypes = {
    item: PropTypes.shape({
        authors: PropTypes.arrayOf(PropTypes.shape({
            code: PropTypes.string.isRequired,
            name: PropTypes.string.isRequired,
            role: PropTypes.string.isRequired,
            biography: PropTypes.string,
        })),
    }),
};
