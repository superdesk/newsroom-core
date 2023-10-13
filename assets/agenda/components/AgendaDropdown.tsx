import React from 'react';
import {gettext} from 'utils';
import {Dropdown} from '../../components/Dropdown';

interface IProps {
    filter: any;
    optionLabel?: string;
    label?: string;
    activeFilter?: any;
    toggleFilter: (filedName: string, value: any) => void;
    getFilterLabel?: (filter: string, activeFilter: string, isActive: boolean) => string;
    children?: any;
    borderless?: boolean;
    dropdownMenuHeader?: string;
    resetOptionLabel?: string;
    hideLabelOnMobile?: boolean;
}

export function AgendaDropdown({
    filter,
    optionLabel,
    activeFilter,
    toggleFilter,
    children,
    getFilterLabel,
    borderless,
    dropdownMenuHeader,
    hideLabelOnMobile,
    
    // Choose a custom label for the reset button
    // if it's not provided it falls back to the filter label
    resetOptionLabel,
}: IProps) {

    const isActive = activeFilter[filter.field];
    const getActiveFilterLabel = getFilterLabel != null ?
        getFilterLabel :
        (filter: any, activeFilter: any, isActive: any) => {
            return isActive ? gettext(activeFilter[filter.field][0]) : gettext(filter.label);
        };

    return (
        <Dropdown
            borderless={borderless}
            isActive={isActive}
            icon={filter.icon}
            optionLabel={optionLabel}
            label={getActiveFilterLabel(filter, activeFilter, isActive)}
            dropdownMenuHeader={dropdownMenuHeader}
            hideLabelOnMobile={hideLabelOnMobile}
        >
            {isActive ? (
                <>
                    <button
                        type='button'
                        className='dropdown-item dropdown-item--emphasized'
                        onClick={() => toggleFilter(filter.field, null)}
                    >
                        {resetOptionLabel ?? gettext(filter.label)}
                    </button>
                </>
            ) : null}
            {children}
        </Dropdown>
    );
}
