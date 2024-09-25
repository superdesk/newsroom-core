import React from 'react';
import Toggle from 'react-toggle';
import classNames from 'classnames';
import 'react-toggle/style.css';
import {useState} from 'react';
import AdvancedSearch from '../components/AdvancedSearch';
import AdvancedSearchTips from '../components/AdvancedSearchTips';
import {RadioButtonGroup} from '../../../assets/features/sections/SectionSwitch.tsx';
import {ContentDivider} from 'ui/components/ContentDivider';
//import { useNavigate } from 'react-router-dom';

function Drafts() {
    return (
        <div className="nh-login-page__content">
            <div className="login-box">
                <div className="">
                    <div className='color-swatches'>
                        <span style={{background: 'var(--morocco-red-100)'}}></span> 
                        <span style={{background: 'var(--morocco-red-200)'}}></span> 
                        <span style={{background: 'var(--morocco-red-300)'}}></span> 
                        <span style={{background: 'var(--morocco-red-400)'}}></span> 
                        <span style={{background: 'var(--morocco-red-500)', color: 'white'}}>base</span> 
                        <span style={{background: 'var(--morocco-red-600)'}}></span> 
                        <span style={{background: 'var(--morocco-red-700)'}}></span> 
                        <span style={{background: 'var(--morocco-red-800)'}}></span> 
                    </div>
                    <div className='color-swatches mt-'>
                        <span style={{background: 'var(--morocco-red-500-a12)', color: 'var(--morocco-red-700)'}}>Text</span> 
                        <span style={{background: 'var(--morocco-red-500-a16)', color: 'var(--morocco-red-700)'}}>Text</span> 
                        <span style={{background: 'var(--morocco-red-500-a24)', color: 'var(--morocco-red-700)'}}>Text</span> 
                        <span style={{background: 'var(--morocco-red-500-a32)', color: 'var(--morocco-red-700)'}}>Text</span> 
                    </div>

                    <div className='color-swatches mt-3'>
                        <span style={{background: 'var(--syrah-soil-100)'}}></span> 
                        <span style={{background: 'var(--syrah-soil-200)'}}></span> 
                        <span style={{background: 'var(--syrah-soil-300)'}}></span> 
                        <span style={{background: 'var(--syrah-soil-400)'}}></span> 
                        <span style={{background: 'var(--syrah-soil-500)', color: 'white'}}>base</span> 
                        <span style={{background: 'var(--syrah-soil-600)'}}></span> 
                        <span style={{background: 'var(--syrah-soil-700)'}}></span> 
                        <span style={{background: 'var(--syrah-soil-800)'}}></span> 
                    </div>
                    <div className='color-swatches mt-'>
                        <span style={{background: 'var(--syrah-soil-500-a12)', color: 'var(--syrah-soil-700)'}}>Text</span> 
                        <span style={{background: 'var(--syrah-soil-500-a16)', color: 'var(--syrah-soil-700)'}}>Text</span> 
                        <span style={{background: 'var(--syrah-soil-500-a24)', color: 'var(--syrah-soil-700)'}}>Text</span> 
                        <span style={{background: 'var(--syrah-soil-500-a32)', color: 'var(--syrah-soil-700)'}}>Text</span> 
                    </div>
                    
                    <div className='color-swatches mt-3'>
                        <span style={{background: 'var(--green-brier-100)'}}></span>
                        <span style={{background: 'var(--green-brier-200)'}}></span> 
                        <span style={{background: 'var(--green-brier-300)'}}></span> 
                        <span style={{background: 'var(--green-brier-400)'}}></span> 
                        <span style={{background: 'var(--green-brier-500)', color: 'white'}}>base</span> 
                        <span style={{background: 'var(--green-brier-600)'}}></span> 
                        <span style={{background: 'var(--green-brier-700)'}}></span> 
                        <span style={{background: 'var(--green-brier-800)'}}></span> 
                    </div>
                    <div className='color-swatches mt-'>
                        <span style={{background: 'var(--green-brier-500-a12)', color: 'var(--green-brier-700)'}}>Text</span> 
                        <span style={{background: 'var(--green-brier-500-a16)', color: 'var(--green-brier-700)'}}>Text</span> 
                        <span style={{background: 'var(--green-brier-500-a24)', color: 'var(--green-brier-700)'}}>Text</span> 
                        <span style={{background: 'var(--green-brier-500-a32)', color: 'var(--green-brier-700)'}}>Text</span> 
                    </div>

                    <div className='color-swatches mt-3'>
                        <span style={{background: 'var(--sorcerer-blue-100)'}}></span> 
                        <span style={{background: 'var(--sorcerer-blue-200)'}}></span> 
                        <span style={{background: 'var(--sorcerer-blue-300)'}}></span> 
                        <span style={{background: 'var(--sorcerer-blue-400)'}}></span> 
                        <span style={{background: 'var(--sorcerer-blue-500)', color: 'white'}}>base</span> 
                        <span style={{background: 'var(--sorcerer-blue-600)'}}></span> 
                        <span style={{background: 'var(--sorcerer-blue-700)'}}></span> 
                        <span style={{background: 'var(--sorcerer-blue-800)'}}></span> 
                    </div>
                    <div className='color-swatches mt-'>
                        <span style={{background: 'var(--sorcerer-blue-500-a12)', color: 'var(--sorcerer-blue-700)'}}>Text</span> 
                        <span style={{background: 'var(--sorcerer-blue-500-a16)', color: 'var(--sorcerer-blue-700)'}}>Text</span> 
                        <span style={{background: 'var(--sorcerer-blue-500-a24)', color: 'var(--sorcerer-blue-700)'}}>Text</span> 
                        <span style={{background: 'var(--sorcerer-blue-500-a32)', color: 'var(--sorcerer-blue-700)'}}>Text</span> 
                    </div>

                    <div className='color-swatches mt-3'>
                        <span style={{background: 'var(--palatinate-blue-100)'}}></span> 
                        <span style={{background: 'var(--palatinate-blue-200)'}}></span> 
                        <span style={{background: 'var(--palatinate-blue-300)'}}></span> 
                        <span style={{background: 'var(--palatinate-blue-400)'}}></span> 
                        <span style={{background: 'var(--palatinate-blue-500)', color: 'white'}}>base</span> 
                        <span style={{background: 'var(--palatinate-blue-600)'}}></span> 
                        <span style={{background: 'var(--palatinate-blue-700)'}}></span> 
                        <span style={{background: 'var(--palatinate-blue-800)'}}></span> 
                    </div>
                    <div className='color-swatches mt-'>
                        <span style={{background: 'var(--palatinate-blue-500-a12)', color: 'var(--palatinate-blue-700)'}}>Text</span> 
                        <span style={{background: 'var(--palatinate-blue-500-a16)', color: 'var(--palatinate-blue-700)'}}>Text</span> 
                        <span style={{background: 'var(--palatinate-blue-500-a24)', color: 'var(--palatinate-blue-700)'}}>Text</span> 
                        <span style={{background: 'var(--palatinate-blue-500-a32)', color: 'var(--palatinate-blue-700)'}}>Text</span> 
                    </div>

                    <div className='color-swatches mt-3'>
                        <span style={{background: 'var(--purple-spot-100)'}}></span> 
                        <span style={{background: 'var(--purple-spot-200)'}}></span> 
                        <span style={{background: 'var(--purple-spot-300)'}}></span> 
                        <span style={{background: 'var(--purple-spot-400)'}}></span> 
                        <span style={{background: 'var(--purple-spot-500)', color: 'white'}}>base</span> 
                        <span style={{background: 'var(--purple-spot-600)'}}></span> 
                        <span style={{background: 'var(--purple-spot-700)'}}></span> 
                        <span style={{background: 'var(--purple-spot-800)'}}></span> 
                    </div>
                    <div className='color-swatches mt-'>
                        <span style={{background: 'var(--purple-spot-500-a12)', color: 'var(--purple-spot-700)'}}>Text</span> 
                        <span style={{background: 'var(--purple-spot-500-a16)', color: 'var(--purple-spot-700)'}}>Text</span> 
                        <span style={{background: 'var(--purple-spot-500-a24)', color: 'var(--purple-spot-700)'}}>Text</span> 
                        <span style={{background: 'var(--purple-spot-500-a32)', color: 'var(--purple-spot-700)'}}>Text</span> 
                    </div>

                    <div className='color-swatches mt-3'>
                        <span style={{background: 'var(--blissful-berry-100)'}}></span> 
                        <span style={{background: 'var(--blissful-berry-200)'}}></span> 
                        <span style={{background: 'var(--blissful-berry-300)'}}></span> 
                        <span style={{background: 'var(--blissful-berry-400)'}}></span> 
                        <span style={{background: 'var(--blissful-berry-500)', color: 'white'}}>base</span> 
                        <span style={{background: 'var(--blissful-berry-600)'}}></span> 
                        <span style={{background: 'var(--blissful-berry-700)'}}></span> 
                        <span style={{background: 'var(--blissful-berry-800)'}}></span> 
                    </div>
                    <div className='color-swatches mt-'>
                        <span style={{background: 'var(--blissful-berry-500-a12)', color: 'var(--blissful-berry-700)'}}>Text</span> 
                        <span style={{background: 'var(--blissful-berry-500-a16)', color: 'var(--blissful-berry-700)'}}>Text</span> 
                        <span style={{background: 'var(--blissful-berry-500-a24)', color: 'var(--blissful-berry-700)'}}>Text</span> 
                        <span style={{background: 'var(--blissful-berry-500-a32)', color: 'var(--blissful-berry-700)'}}>Text</span> 
                    </div>
                </div>
            </div>
        </div>
    );
  }
  
  export default Drafts;
  