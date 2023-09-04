/* eslint-disable react/prop-types */
import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import classNames from 'classnames';

import {selectSection} from './actions';
import {sectionsPropType} from './types';
import {assertNever, gettext} from '../../utils';

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

interface IProps {
    options: Array<{_id: string, name: string}>;
    switchOptions: (optionId: string) => void;
    activeOptionId: string;
    size?: 'small' | 'large'; // defaults to large
    fullWidth?: boolean;
    gap?: boolean;
    className?: string;
}

export const RadioButtonGroup: React.ComponentType<IProps> = (props) => {
    const {options, switchOptions, activeOptionId, fullWidth, gap, className} = props;

    const wrapperClasses = classNames('toggle-button__group', {
        'toggle-button__group--spaced': gap,
        'toggle-button__group--stretch-items w-100': fullWidth,
        [`${className}`]: className,
    });

    const size: IProps['size'] = props.size ?? 'large';

    const classList = ['toggle-button'];

    if (size === 'large') {
        classList.push('toggle-button--large');
    } else if (size === 'small') {
        classList.push('toggle-button--small');
    } else {
        assertNever(size);
    }

    return (
        <div className={wrapperClasses}>
            {
                options.map((section: any) => {
                    const buttonClasses = classNames(classList, {
                        'toggle-button--active': section._id === activeOptionId,
                    });

                    return (
                        <button
                            key={section._id}
                            className={buttonClasses}
                            onClick={() => switchOptions(section._id)}
                        >
                            {gettext(section.name)}
                        </button>
                    );
                })
            }
        </div>
    );
};

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
