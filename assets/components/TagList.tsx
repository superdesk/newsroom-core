import React from 'react';
import PropTypes from 'prop-types';
import {get} from 'lodash';

import {Tag} from './Tag';

export default function TagList({tags, onClick, readOnly}: any) {
    return ((get(tags, 'length', 0) > 0 && <div className='tag-list'>
        <ul>
            {tags.map((t, index) => (
                <Tag
                    key={index}
                    text={t}
                    readOnly={readOnly}
                    onClick={onClick}
                />
            ))}
        </ul>
    </div>) || null);
}

TagList.propTypes = {
    tags: PropTypes.array,
    onClick: PropTypes.func,
    readOnly: PropTypes.bool,
};
