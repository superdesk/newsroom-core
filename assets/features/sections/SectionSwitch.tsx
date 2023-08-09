import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';

import {selectSection} from './actions';
import {sectionsPropType} from './types';
import {gettext} from '../../utils';

function SectionSwitch({sections, activeSection, selectSection}: any) {
    return (
        <div className="toggle-button__group toggle-button__group--navbar ms-0 me-3">
            {sections.map((section: any) => (
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

const mapDispatchToProps: any = {
    selectSection,
};

const component: React.ComponentType<any> = connect(null, mapDispatchToProps)(SectionSwitch);

export default component;
