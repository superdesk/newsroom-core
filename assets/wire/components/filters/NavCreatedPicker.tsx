import React from 'react';
import PropTypes from 'prop-types';
import {gettext} from 'utils';

import NavLink from './NavLink';
import NavGroup from './NavGroup';

const shortcuts = [
    {label: gettext('Today'), value: 'now/d'},
    {label: gettext('This week'), value: 'now/w'},
    {label: gettext('This month'), value: 'now/M'},
];

function NavCreatedPicker({setCreatedFilter, createdFilter, context}: any) {
    const onClickFactory = (value: any) => (event: any) => {
        event.preventDefault();
        setCreatedFilter({from: createdFilter.from === value ? null : value, to: null});
    };

    const onInputChange = (event: any) => {
        setCreatedFilter({[event.target.name]: event.target.value});
    };

    const activeShortcut = shortcuts.find((shortcut: any) => shortcut.value === createdFilter.from);

    return (
        <NavGroup label={context === 'agenda' ? (gettext('Event Date')) : (gettext('Published'))}>
            <div className='nh-button__group nh-button__group--vertical mb-2'>
                {shortcuts.map((shortcut) => (
                    <NavLink key={shortcut.value}
                        label={shortcut.label}
                        onClick={onClickFactory(shortcut.value)}
                        isActive={shortcut === activeShortcut}
                    />
                ))}
            </div>
            <div className="formGroup mb-2">
                <label htmlFor="created-from">{gettext('From')}</label>
                <input id="created-from" type="date" name="from"
                    className="form-control"
                    onChange={onInputChange}
                    value={activeShortcut ? '' : createdFilter.from || ''}
                />
            </div>
            <div className="formGroup">
                <label htmlFor="created-to">{gettext('To')}</label>
                <input id="created-to" type="date" name="to"
                    className="form-control"
                    onChange={onInputChange}
                    value={createdFilter.to || ''}
                />
            </div>
        </NavGroup>
    );
}

NavCreatedPicker.propTypes = {
    createdFilter: PropTypes.object.isRequired,
    setCreatedFilter: PropTypes.func.isRequired,
    context: PropTypes.string,
};

export default NavCreatedPicker;
