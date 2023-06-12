import React from 'react';
import PropTypes from  'prop-types';
import {gettext} from '../utils';


export default function BookmarkTabs(props: any) {
    const sections = Object.keys(props.sections).map((id) => {
        const section = props.sections[id];

        return <a key={section._id}
            className={'toggle-button' + (section._id === props.active ? ' toggle-button--active' : '')}
            href={`/bookmarks_${section._id}`}>{gettext(section.name)}</a>;
    });

    if (sections.length < 2) {
        return null;
    }

    return (
        <div className="toggle-button__group toggle-button__group--navbar ms-3 me-3">
            {sections}
        </div>
    );
}

BookmarkTabs.propTypes = {
    active: PropTypes.string.isRequired,
    sections: PropTypes.object.isRequired,
};