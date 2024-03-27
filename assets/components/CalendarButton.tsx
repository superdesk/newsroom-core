import React from 'react';
import PropTypes from 'prop-types';
import {gettext} from 'utils';
import DatePicker from 'react-datepicker';
import moment from 'moment';
import CalendarButtonWrapper from './CalendarButtonWrapper';
import {EARLIEST_DATE} from '../agenda/utils';
import {registerLocale} from  'react-datepicker';
import * as locales from 'date-fns/locale';

class CalendarButton extends React.Component<any, any> {
    static propTypes: any;
    constructor (props: any) {
        super(props);

        this.state = {startDate: moment(this.props.activeDate).toDate()};
        this.handleChange = this.handleChange.bind(this);
    }

    handleChange(date: any) {
        this.props.selectDate(date.valueOf(), 'day');
        this.setState({startDate: date});
    }

    componentDidUpdate(prevProps: any) {
        prevProps.activeDate === EARLIEST_DATE && this.setState({startDate: moment(this.props.activeDate)});
    }

    getLocale = () => {
        const locale = window.locale.replace('_', '');
        const rootLocale = locale.substring(0, 2);
        const allLocales = locales as any;

        return allLocales[locale] ?? allLocales[rootLocale];
    };

    render() {
        const locale = this.getLocale();

        if (locale != undefined) {
            registerLocale(locale.code, locale);
        }

        const isStartDateToday = moment.isMoment(this.state.startDate) && !this.state.startDate.isSame(moment(), 'day');
        const datePicker = (
            <DatePicker
                customInput={<CalendarButtonWrapper active={isStartDateToday}/>}
                dateFormat="yyyy-MM-dd"
                todayButton={gettext('Today')}
                selected={this.state.startDate}
                onChange={this.handleChange}
                highlightDates={[moment().toDate()]}
                locale={locale?.code ?? 'en'}
                popperModifiers={[
                    {
                        name: 'offset',
                        options: {
                            offset: [5, 10],
                        },
                    },
                ]}
            />
        );

        if (!this.props.label) {
            return datePicker;
        } else {
            return (
                <div className={this.props.labelClass}>
                    <label className='pe-1 label--no-spacing'>{this.props.label}</label>
                    {datePicker}
                </div>
            );

        }
    }
}

CalendarButton.propTypes = {
    selectDate: PropTypes.func,
    activeDate: PropTypes.number,
    label: PropTypes.string,
    labelClass: PropTypes.string,
};

export default CalendarButton;
