import React from 'react';

import AgendaDateButtons from './AgendaDateButtons';
import CalendarButton from '../../components/CalendarButton';

interface IProps {
    selectDate: any;
    activeDate: number;
    activeGrouping: string;
    displayCalendar: boolean;
}

function AgendaDateNavigation({selectDate, activeDate, activeGrouping, displayCalendar}: IProps) {
    return (<div className='d-none d-lg-flex align-items-center me-3'>
        {displayCalendar && <CalendarButton selectDate={selectDate} activeDate={activeDate} />}

        {!displayCalendar && <AgendaDateButtons
            selectDate={selectDate} activeDate={activeDate} activeGrouping={activeGrouping}/>}
    </div>);
}

export default AgendaDateNavigation;
