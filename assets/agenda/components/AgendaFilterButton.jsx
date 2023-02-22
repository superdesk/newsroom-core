import React from 'react';
import PropTypes from 'prop-types';
import {gettext} from 'utils';

import DropdownFilterButton from 'components/DropdownFilterButton';

const getActiveFilterLabel = (filter, activeFilter, isActive) => {
    return isActive ? gettext(activeFilter[filter.field][0]) : gettext(filter.label);
};

function AgendaFilterButton({filter, activeFilter, autoToggle, onClick}) {
    const isActive = (activeFilter[filter.field] || []).length > 0;

    return (
        <DropdownFilterButton
            id={filter.field}
            isActive={isActive}
            autoToggle={autoToggle}
            onClick={onClick}
            icon={filter.icon}
            label={getActiveFilterLabel(filter, activeFilter, isActive)}
        />
    );
}

AgendaFilterButton.propTypes = {
    filter: PropTypes.object,
    activeFilter: PropTypes.object,
    autoToggle: PropTypes.bool,
    onClick: PropTypes.func,
};

AgendaFilterButton.defaultProps = {autoToggle: true};

export default AgendaFilterButton;
