# -*- coding: utf-8 -*-
import logging

try:
    from odoo.models import OneshareHyperModel as HModel
except ImportError:
    from odoo.models import Model as HModel

_logger = logging.getLogger(__name__)


class OperationResult(HModel):
    """
    默认结果类型为拧紧
    """
    _inherit = "onesphere.tightening.result"

    # FIXME: 无工单模式存储过程
    def init(self):
        self.env.cr.execute("""
        CREATE OR REPLACE FUNCTION create_operation_tightening_result (
                control_date TIMESTAMP WITHOUT TIME ZONE,
                user_id BIGINT,
                pset_strategy VARCHAR,
                cur_objects VARCHAR,
                measure_result varchar,
                measure_degree NUMERIC,
                measure_torque NUMERIC,
                exception_reason VARCHAR,
                batch VARCHAR,
                r_tightening_id VARCHAR,
                gun_sn VARCHAR, 
                vin_code VARCHAR,
                r_pset VARCHAR,
                measurement_step_results VARCHAR,
                tightening_unit_code VARCHAR,
                tightening_point_name VARCHAR,
                workcenter_code VARCHAR,
                barcode varchar, 
                track_img_url varchar, 
                measure_rule_result varchar,
                step_type varchar,
                work_mode varchar,
                user_list varchar
            ) RETURNS BIGINT AS 
            $$ 
            DECLARE
            r_measure_result VARCHAR;
            result_id BIGINT;
            user_name_list VARCHAR;
            bolt_id BIGINT;
            BEGIN

                case pset_strategy
                    when 'LN'
                        then r_measure_result = 'lsn';
                    ELSE r_measure_result = measure_result;
                    end case;

                case when user_list = ''
                then user_name_list = null;
                else select string_agg(user_name,',') into user_name_list from 
                (select json_array_elements(user_list::json) ->> 'name' user_name)user_info;
                end case;

                select id into bolt_id from onesphere_tightening_bolt where name=tightening_point_name;

                if bolt_id is null then insert into onesphere_tightening_bolt (name,type)
                values(tightening_point_name,'missing') returning id into bolt_id;
                end if;

                INSERT INTO PUBLIC.onesphere_tightening_result (
                track_no,
                attribute_equipment_no,
                tightening_process_no,
                tightening_strategy,
                tightening_result,
                measurement_final_torque,
                measurement_final_angle,
                measurement_step_results,
                tightening_id,
                error_code,
                curve_file,
                control_time,
                tightening_unit_code,
                tightening_point_name,
                user_id,
                workcenter_code,
                batch,
                time,
                barcode,
                track_img_url,
                measure_rule_result,
                step_type,
                work_mode,
                user_list
                )
            VALUES(   
                    vin_code,
                    gun_sn,
                    r_pset,
                    pset_strategy,
                    r_measure_result,
                    measure_torque,
                    measure_degree,
                    measurement_step_results,
                    r_tightening_id,
                    exception_reason,
                    cur_objects,
                    control_date,
                    tightening_unit_code,
                    bolt_id,
                    user_id,
                    workcenter_code,
                    batch,
                    now(),
                    barcode,
                    track_img_url,
                    measure_rule_result,
                    'tightening',
                    work_mode,
                    user_name_list
                );
            result_id = lastval( );
            RETURN result_id;

        END;
        $$ LANGUAGE plpgsql;
        """)
