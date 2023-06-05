import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';

import {selectSection} from './actions';
import {sectionsPropType} from './types';
import {gettext} from '../../utils';

function SectionSwitch({sections, activeSection, selectSection}) {
    return (
        <div className="toggle-button__group toggle-button__group--navbar ms-0 me-3">
            {sections.map((section) => (
                <button key={section._id}
                    className={'toggle-button' + (section._id === activeSection ? ' toggle-button--active' : '')}
                    onClick={() => selectSection(section._id)}
                >{gettext(section.name)}</button>
            ))}
        </div>
    );
}

SectionSwitch.propTypes = {
    sections: sectionsPropType,
    activeSection: PropTypes.string,

    selectSection: PropTypes.func.isRequired,
};

const mapDispatchToProps = {
    selectSection,
};

export default connect(null, mapDispatchToProps)(SectionSwitch);